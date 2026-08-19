from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import Session, select

from ..config import get_settings
from ..models import ActionRequest, Agent, Approval, ApprovalStatus, Policy, ProtectedResource, User, utcnow
from ..schemas import DecisionRequest
from .audit import write_audit_event
from .policy_engine import PolicyEngine

settings = get_settings()
policy_engine = PolicyEngine()


@dataclass
class GovernanceResult:
    action_request: ActionRequest
    approval: Approval | None
    matched_policy_name: str | None


def evaluate_and_record(payload: DecisionRequest, user: User, session: Session) -> GovernanceResult:
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
    # Authorization uses the authenticated identity; callers cannot spoof user_email.
    request["user_email"] = user.email
    decision = policy_engine.evaluate(policies=policies, request=request)
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

    approval = None
    if decision.decision == "requires_approval":
        approval = Approval(
            organization_id=user.organization_id,
            action_request_id=action_request.id,
            status=ApprovalStatus.pending,
            expires_at=utcnow() + timedelta(minutes=settings.approval_ttl_minutes),
        )
        session.add(approval)
        session.commit()
        session.refresh(approval)

    write_audit_event(
        session,
        user=user,
        event_type="policy_decision",
        result=decision.decision,
        message=decision.reason,
        correlation_id=correlation_id,
        metadata={
            "action_request_id": action_request.id,
            "approval_id": approval.id if approval else None,
            "agent_name": payload.agent_name,
            "action": payload.action,
            "resource_name": payload.resource_name,
            "environment": payload.environment,
            "matched_policy_id": decision.matched_policy_id,
            "evaluated_policy_count": decision.evaluated_policy_count,
        },
    )

    return GovernanceResult(
        action_request=action_request,
        approval=approval,
        matched_policy_name=decision.matched_policy_name,
    )
