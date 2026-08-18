from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import ActionRequest, Approval, ApprovalStatus, Role, User
from ..schemas import ApprovalDecision
from ..security import require_roles
from ..services.audit import write_audit_event

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
def list_approvals(user: User = Depends(require_roles(Role.admin, Role.approver, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(Approval).where(Approval.organization_id == user.organization_id).order_by(Approval.created_at.desc())).all()


@router.get("/{approval_id}")
def get_approval(approval_id: int, user: User = Depends(require_roles(Role.admin, Role.approver, Role.auditor)), session: Session = Depends(get_session)):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    action_request = session.get(ActionRequest, approval.action_request_id)
    return {
        "id": approval.id,
        "organization_id": approval.organization_id,
        "action_request_id": approval.action_request_id,
        "status": approval.status,
        "reviewer_email": approval.reviewer_email,
        "reviewer_notes": approval.reviewer_notes,
        "reviewed_at": approval.reviewed_at,
        "created_at": approval.created_at,
        "action_request": action_request,
    }


def _assert_no_self_approval(user: User, action_request: ActionRequest | None):
    if action_request and user.email == action_request.user_email:
        raise HTTPException(status_code=403, detail="Self-approval is not allowed")


def _review(approval_id: int, status: ApprovalStatus, payload: ApprovalDecision, user: User, session: Session):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=409, detail="Approval already processed")

    action_request = session.get(ActionRequest, approval.action_request_id)
    _assert_no_self_approval(user, action_request)

    approval.status = status
    approval.reviewer_email = user.email
    approval.reviewer_notes = payload.notes
    approval.reviewed_at = datetime.utcnow()
    session.add(approval)
    session.commit()
    session.refresh(approval)

    write_audit_event(
        session,
        user=user,
        event_type="approval_review",
        result=status.value,
        message=f"Approval {approval.id} was {status.value}.",
        metadata={"approval_id": approval.id, "action_request_id": approval.action_request_id},
    )
    return approval


@router.post("/{approval_id}/approve")
def approve(approval_id: int, payload: ApprovalDecision, user: User = Depends(require_roles(Role.approver, Role.admin)), session: Session = Depends(get_session)):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    action_request = session.get(ActionRequest, approval.action_request_id)
    _assert_no_self_approval(user, action_request)
    return _review(approval_id, ApprovalStatus.approved, payload, user, session)


@router.post("/{approval_id}/reject")
def reject(approval_id: int, payload: ApprovalDecision, user: User = Depends(require_roles(Role.approver, Role.admin)), session: Session = Depends(get_session)):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    action_request = session.get(ActionRequest, approval.action_request_id)
    _assert_no_self_approval(user, action_request)
    return _review(approval_id, ApprovalStatus.rejected, payload, user, session)


@router.post("/{approval_id}/expire")
def expire(approval_id: int, payload: ApprovalDecision, user: User = Depends(require_roles(Role.approver, Role.admin, Role.auditor)), session: Session = Depends(get_session)):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    action_request = session.get(ActionRequest, approval.action_request_id)
    _assert_no_self_approval(user, action_request)
    return _review(approval_id, ApprovalStatus.expired, payload, user, session)


@router.post("/{approval_id}/cancel")
def cancel(approval_id: int, payload: ApprovalDecision, user: User = Depends(require_roles(Role.admin, Role.approver)), session: Session = Depends(get_session)):
    approval = session.get(Approval, approval_id)
    if not approval or approval.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    action_request = session.get(ActionRequest, approval.action_request_id)
    _assert_no_self_approval(user, action_request)
    return _review(approval_id, ApprovalStatus.cancelled, payload, user, session)
