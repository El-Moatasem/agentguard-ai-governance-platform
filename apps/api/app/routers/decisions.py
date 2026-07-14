from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import ActionRequest, Approval, ApprovalStatus, Policy, Role, User
from ..schemas import DecisionRequest, DecisionResponse
from ..security import require_roles
from ..services.audit import write_audit_event
from ..services.policy_engine import PolicyEngine

router = APIRouter(prefix="/decisions", tags=["decisions"])
engine = PolicyEngine()


@router.post("/evaluate", response_model=DecisionResponse)
def evaluate_action(payload: DecisionRequest, user: User = Depends(require_roles(Role.admin, Role.developer)), session: Session = Depends(get_session)):
    policies = session.exec(select(Policy).where(Policy.organization_id == user.organization_id)).all()
    request = payload.model_dump()
    decision = engine.evaluate(policies=policies, request=request)

    action_request = ActionRequest(
        organization_id=user.organization_id,
        **request,
        decision=decision.decision,
        reason=decision.reason,
        matched_policy_id=decision.matched_policy_id,
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
        metadata={"action_request_id": action_request.id, "approval_id": approval_id},
    )

    return DecisionResponse(
        decision=decision.decision,
        reason=decision.reason,
        matched_policy_id=decision.matched_policy_id,
        action_request_id=action_request.id,
        approval_id=approval_id,
    )
