from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import ActionRequest, Role, User
from ..schemas import ActionRequestOut, DecisionRequest, DecisionResponse
from ..security import require_roles
from ..services.governance import evaluate_and_record

router = APIRouter(prefix="/decisions", tags=["decisions"])


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
    result = evaluate_and_record(payload, user, session)
    request = result.action_request
    return DecisionResponse(
        correlation_id=request.correlation_id,
        decision=request.decision,
        reason=request.reason,
        matched_policy_id=request.matched_policy_id,
        matched_policy_name=result.matched_policy_name,
        evaluated_policy_count=request.evaluated_policy_count,
        action_request_id=request.id,
        approval_id=result.approval.id if result.approval else None,
    )
