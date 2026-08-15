from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import ActionRequest, Approval, ApprovalStatus, ExecutionStatus, Role, ToolExecution, User, utcnow
from ..schemas import ActionRequestOut, ApprovalDecision, ApprovalDetail, ApprovalOut, ToolExecutionOut
from ..security import require_roles
from ..services.audit import write_audit_event
from ..services.tool_execution import run_execution

router = APIRouter(prefix="/approvals", tags=["approvals"])


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _expire_if_needed(approval: Approval, session: Session) -> bool:
    if approval.status != ApprovalStatus.pending or not approval.expires_at:
        return False
    if _aware(approval.expires_at) > utcnow():
        return False
    approval.status = ApprovalStatus.expired
    approval.reviewed_at = utcnow()
    approval.updated_at = utcnow()
    execution = session.exec(select(ToolExecution).where(ToolExecution.action_request_id == approval.action_request_id)).first()
    if execution and execution.status == ExecutionStatus.pending_approval:
        execution.status = ExecutionStatus.cancelled
        execution.error_message = "Approval expired before execution"
        execution.completed_at = utcnow()
        execution.updated_at = utcnow()
        session.add(execution)
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return True


def _get_approval(approval_id: int, user: User, session: Session) -> Approval:
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    _expire_if_needed(approval, session)
    return approval


@router.get("", response_model=list[ApprovalOut])
def list_approvals(
    status: ApprovalStatus | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(require_roles(Role.admin, Role.approver, Role.auditor)),
    session: Session = Depends(get_session),
):
    pending = session.exec(select(Approval).where(Approval.organization_id == user.organization_id, Approval.status == ApprovalStatus.pending)).all()
    for approval in pending:
        _expire_if_needed(approval, session)

    statement = select(Approval).where(Approval.organization_id == user.organization_id)
    if status:
        statement = statement.where(Approval.status == status)
    return session.exec(statement.order_by(Approval.created_at.desc()).offset(skip).limit(limit)).all()


@router.get("/{approval_id}/detail", response_model=ApprovalDetail)
def get_approval_detail(
    approval_id: int,
    user: User = Depends(require_roles(Role.admin, Role.approver, Role.auditor)),
    session: Session = Depends(get_session),
):
    approval = _get_approval(approval_id, user, session)
    action_request = session.get(ActionRequest, approval.action_request_id)
    if not action_request:
        raise HTTPException(status_code=404, detail="Action request not found")
    execution = session.exec(select(ToolExecution).where(ToolExecution.action_request_id == action_request.id)).first()
    return ApprovalDetail(
        approval=ApprovalOut.model_validate(approval, from_attributes=True),
        action_request=ActionRequestOut.model_validate(action_request, from_attributes=True),
        execution=ToolExecutionOut.model_validate(execution, from_attributes=True) if execution else None,
    )


@router.get("/{approval_id}", response_model=ApprovalOut)
def get_approval(
    approval_id: int,
    user: User = Depends(require_roles(Role.admin, Role.approver, Role.auditor)),
    session: Session = Depends(get_session),
):
    return _get_approval(approval_id, user, session)


def _review(approval_id: int, status: ApprovalStatus, payload: ApprovalDecision, user: User, session: Session):
    approval = _get_approval(approval_id, user, session)
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=409, detail=f"Approval is already {approval.status.value}")

    action_request = session.get(ActionRequest, approval.action_request_id)
    if not action_request:
        raise HTTPException(status_code=404, detail="Action request not found")
    if action_request.user_email.lower() == user.email.lower():
        raise HTTPException(status_code=403, detail="Requesters cannot approve or reject their own governed action")

    approval.status = status
    approval.reviewer_email = user.email
    approval.reviewer_notes = payload.notes
    approval.reviewed_at = utcnow()
    approval.updated_at = utcnow()
    session.add(approval)
    session.commit()
    session.refresh(approval)

    write_audit_event(
        session,
        user=user,
        event_type="approval_review",
        result=status.value,
        message=f"Approval {approval.id} was {status.value}.",
        correlation_id=action_request.correlation_id,
        metadata={"approval_id": approval.id, "action_request_id": approval.action_request_id},
    )

    execution = session.exec(select(ToolExecution).where(ToolExecution.action_request_id == approval.action_request_id)).first()
    if execution:
        if status == ApprovalStatus.approved and execution.status == ExecutionStatus.pending_approval:
            run_execution(session, execution, user)
        elif status == ApprovalStatus.rejected and execution.status == ExecutionStatus.pending_approval:
            execution.status = ExecutionStatus.cancelled
            execution.error_message = "Execution rejected by human approver"
            execution.completed_at = utcnow()
            execution.updated_at = utcnow()
            session.add(execution)
            session.commit()
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalOut)
def approve(
    approval_id: int,
    payload: ApprovalDecision,
    user: User = Depends(require_roles(Role.approver, Role.admin)),
    session: Session = Depends(get_session),
):
    return _review(approval_id, ApprovalStatus.approved, payload, user, session)


@router.post("/{approval_id}/reject", response_model=ApprovalOut)
def reject(
    approval_id: int,
    payload: ApprovalDecision,
    user: User = Depends(require_roles(Role.approver, Role.admin)),
    session: Session = Depends(get_session),
):
    return _review(approval_id, ApprovalStatus.rejected, payload, user, session)


@router.post("/{approval_id}/cancel", response_model=ApprovalOut)
def cancel(
    approval_id: int,
    payload: ApprovalDecision,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    approval = _get_approval(approval_id, user, session)
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=409, detail=f"Approval is already {approval.status.value}")
    action_request = session.get(ActionRequest, approval.action_request_id)
    if not action_request:
        raise HTTPException(status_code=404, detail="Action request not found")
    if user.role != Role.admin and action_request.user_email.lower() != user.email.lower():
        raise HTTPException(status_code=403, detail="Only the requester or an administrator can cancel this approval")

    approval.status = ApprovalStatus.cancelled
    approval.reviewer_email = user.email
    approval.reviewer_notes = payload.notes
    approval.reviewed_at = utcnow()
    approval.updated_at = utcnow()
    session.add(approval)

    execution = session.exec(select(ToolExecution).where(ToolExecution.action_request_id == approval.action_request_id)).first()
    if execution and execution.status == ExecutionStatus.pending_approval:
        execution.status = ExecutionStatus.cancelled
        execution.error_message = "Execution cancelled by requester"
        execution.completed_at = utcnow()
        execution.updated_at = utcnow()
        session.add(execution)
    session.commit()
    session.refresh(approval)

    write_audit_event(
        session,
        user=user,
        event_type="approval_cancelled",
        result="cancelled",
        message=f"Approval {approval.id} was cancelled.",
        correlation_id=action_request.correlation_id,
        metadata={"approval_id": approval.id, "action_request_id": approval.action_request_id},
    )
    return approval
