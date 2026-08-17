from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..models import ActionRequest, Policy, Role, User
from ..schemas import AssistantExplainRequest, DecisionExplanation
from ..security import require_roles
from ..services.ai_provider import explain_decision

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/explain-decision", response_model=DecisionExplanation)
def explain_decision_route(
    payload: AssistantExplainRequest,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    action_request = session.get(ActionRequest, payload.action_request_id)
    if not action_request or action_request.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Action request not found")
    policy = session.get(Policy, action_request.matched_policy_id) if action_request.matched_policy_id else None
    if policy and policy.organization_id != user.organization_id:
        policy = None
    return explain_decision(action_request, policy)


@router.get("/incident-summary")
def summarize_incidents(user: User = Depends(require_roles(Role.admin, Role.auditor))):
    return {
        "summary": "Review denied production attempts, approval queues, failed executions, and MCP activity before release decisions.",
        "recommendations": [
            "Review high-priority deny policies weekly.",
            "Keep sensitive actions in approval-required mode until operational evidence supports automation.",
            "Export audit events and execution traces before stakeholder demonstrations.",
        ],
    }
