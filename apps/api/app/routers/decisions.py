from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..database import get_session
from ..models import ActionRequest, Agent, Approval, ApprovalStatus, Policy, ProtectedResource, Role, User
from ..schemas import ActionRequestOut, DecisionRequest, DecisionResponse
from ..security import require_roles
from ..services.audit import write_audit_event
from ..services.policy_engine import PolicyEngine

router = APIRouter(prefix="/decisions", tags=["decisions"])
engine = PolicyEngine()


@router.get("/requests", response_model=list[ActionRequestOut])
def list_action_requests(
    decision: str | None = None,
    agent_name: str | None = None,
    resource_name: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(ActionRequest).where(ActionRequest.organization_id == user.organization_id)
    if decision:
        statement = statement.where(ActionRequest.decision == decision)
    if agent_name:
        statement = statement.where(ActionRequest.agent_name == agent_name)
    if resource_name:
        statement = statement.where(ActionRequest.resource_name == resource_name)
    return session.exec(statement.order_by(ActionRequest.created_at.desc()).offset(skip).limit(limit)).all()


@router.get("/requests/{request_id}", response_model=ActionRequestOut)
def get_action_request(
    request_id: int,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor, Role.approver)),
    session: Session = Depends(get_session),
):
    action_request = session.get(ActionRequest, request_id)
    if not action_request or action_request.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Action request not found")
    return action_request


@router.post("/evaluate", response_model=DecisionResponse, status_code=201)
def evaluate_action(
    payload: DecisionRequest,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    agent = session.exec(
        select(Agent).where(
            Agent.organization_id == user.organization_id,
            Agent.name == payload.agent_name,
            Agent.status == "active",
        )
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Active agent not found")

    resource = session.exec(
        select(ProtectedResource).where(
            ProtectedResource.organization_id == user.organization_id,
            ProtectedResource.name == payload.resource_name,
        )
    ).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Protected resource not found")

    policies = session.exec(select(Policy).where(Policy.organization_id == user.organization_id)).all()
    request = payload.model_dump()
    decision = engine.evaluate(policies=policies, request=request)
    correlation_id = uuid4().hex

    action_request = ActionRequest(
        organization_id=user.organization_id,
        correlation_id=correlation_id,
        **request,
        decision=decision.decision,
        reason=decision.reason,
        matched_policy_id=decision.matched_policy_id,
        evaluated_policy_count=decision.evaluated_policy_count,
    )
    session.add(action_request)
    session.commit()
    session.refresh(action_request)

    approval_id = None
    if decision.decision == "requires_approval":
        approval = Approval(
            organization_id=user.organization_id,
            action_request_id=action_request.id,
            status=ApprovalStatus.pending,
        )
        session.add(approval)
        session.commit()
        session.refresh(approval)
        approval_id = approval.id

    write_audit_event(
        session,
        user=user,
        event_type="policy_decision",
        result=decision.decision,
        message=decision.reason,
        correlation_id=correlation_id,
        metadata={
            "action_request_id": action_request.id,
            "approval_id": approval_id,
            "agent_name": payload.agent_name,
            "action": payload.action,
            "resource_name": payload.resource_name,
            "environment": payload.environment,
            "matched_policy_id": decision.matched_policy_id,
            "evaluated_policy_count": decision.evaluated_policy_count,
        },
    )

    return DecisionResponse(
        correlation_id=correlation_id,
        decision=decision.decision,
        reason=decision.reason,
        matched_policy_id=decision.matched_policy_id,
        matched_policy_name=decision.matched_policy_name,
        evaluated_policy_count=decision.evaluated_policy_count,
        action_request_id=action_request.id,
        approval_id=approval_id,
    )
