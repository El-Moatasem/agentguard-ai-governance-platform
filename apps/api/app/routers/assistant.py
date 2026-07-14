from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..models import ActionRequest, Role, User
from ..schemas import AssistantExplainRequest
from ..security import require_roles

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/explain-decision")
def explain_decision(payload: AssistantExplainRequest, user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)), session: Session = Depends(get_session)):
    action_request = session.get(ActionRequest, payload.action_request_id)
    if not action_request or action_request.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Action request not found")

    return {
        "summary": (
            f"The request by agent '{action_request.agent_name}' to perform '{action_request.action}' "
            f"on '{action_request.resource_name}' resulted in '{action_request.decision}'."
        ),
        "reason": action_request.reason,
        "safety_note": "This explanation is generated after the deterministic policy decision and cannot override authorization.",
    }


@router.get("/incident-summary")
def summarize_incidents(user: User = Depends(require_roles(Role.admin, Role.auditor))):
    return {
        "summary": "Demo summary: review denied production access attempts and pending approvals for restricted financial data.",
        "recommendations": [
            "Review high-priority deny policies weekly.",
            "Keep sensitive actions in approval-required mode until the risk model is mature.",
            "Export audit events before stakeholder demonstrations.",
        ],
    }
