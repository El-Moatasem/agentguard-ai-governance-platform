from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import ActionRequest, Agent, Approval, ExecutionStatus, Role, Tool, ToolExecution, User
from ..schemas import DecisionRequest, GovernedExecutionResponse, ToolExecutionOut, ToolExecutionRequest
from ..security import require_roles
from ..services.audit import write_audit_event
from ..services.governance import evaluate_and_record
from ..services.security_guardrails import allowed_fields_for_tool, redact_sensitive, validate_tool_arguments
from ..services.tool_execution import create_execution, run_execution

router = APIRouter(prefix="/executions", tags=["governed-execution"])


def submit_governed_execution(payload: ToolExecutionRequest, user: User, session: Session) -> GovernedExecutionResponse:
    validate_tool_arguments(payload.arguments)

    if payload.idempotency_key:
        existing = session.exec(select(ToolExecution).where(ToolExecution.idempotency_key == payload.idempotency_key)).first()
        if existing:
            if existing.organization_id != user.organization_id:
                raise HTTPException(status_code=409, detail="Idempotency key is already in use")
            existing_request = session.get(ActionRequest, existing.action_request_id)
            if not existing_request:
                raise HTTPException(status_code=409, detail="Existing idempotent execution is missing its action request")
            approval = session.exec(select(Approval).where(Approval.action_request_id == existing_request.id)).first()
            return GovernedExecutionResponse(
                correlation_id=existing_request.correlation_id,
                decision=existing_request.decision,
                reason=existing_request.reason,
                action_request_id=existing_request.id,
                approval_id=approval.id if approval else None,
                execution=ToolExecutionOut.model_validate(existing, from_attributes=True),
            )

    agent = session.exec(
        select(Agent).where(
            Agent.organization_id == user.organization_id,
            Agent.name == payload.agent_name,
            Agent.status == "active",
        )
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Active agent not found")

    tool = session.exec(
        select(Tool).where(
            Tool.organization_id == user.organization_id,
            Tool.agent_id == agent.id,
            Tool.name == payload.tool_name,
        )
    ).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Registered tool not found for agent")
    if payload.action not in tool.allowed_actions:
        raise HTTPException(status_code=403, detail="Action is not allowlisted for the selected tool")
    validate_tool_arguments(payload.arguments, allowed_fields_for_tool(tool))

    governance_context = {**payload.arguments, **payload.context, "tool_name": tool.name}
    decision_payload = DecisionRequest(
        agent_name=payload.agent_name,
        user_email=user.email,
        action=payload.action,
        resource_name=payload.resource_name,
        environment=payload.environment,
        context=governance_context,
    )
    result = evaluate_and_record(decision_payload, user, session)
    action_request = result.action_request

    initial_status = {
        "allow": ExecutionStatus.running,
        "deny": ExecutionStatus.blocked,
        "requires_approval": ExecutionStatus.pending_approval,
    }[action_request.decision]

    execution = create_execution(
        session,
        action_request=action_request,
        tool=tool,
        user=user,
        arguments=payload.arguments,
        status=initial_status,
        idempotency_key=payload.idempotency_key or f"ag-{uuid4().hex}",
    )

    if action_request.decision == "allow":
        execution = run_execution(session, execution, user)
    elif action_request.decision == "deny":
        write_audit_event(
            session,
            user=user,
            event_type="tool_execution_blocked",
            result="blocked",
            message=f"Tool execution {execution.id} was blocked by policy.",
            correlation_id=action_request.correlation_id,
            metadata={"execution_id": execution.id, "tool_name": tool.name, "arguments": redact_sensitive(payload.arguments)},
        )

    return GovernedExecutionResponse(
        correlation_id=action_request.correlation_id,
        decision=action_request.decision,
        reason=action_request.reason,
        action_request_id=action_request.id,
        approval_id=result.approval.id if result.approval else None,
        execution=ToolExecutionOut.model_validate(execution, from_attributes=True),
    )


@router.post("", response_model=GovernedExecutionResponse, status_code=201)
def create_governed_execution(
    payload: ToolExecutionRequest,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    return submit_governed_execution(payload, user, session)


@router.get("", response_model=list[ToolExecutionOut])
def list_executions(
    status: ExecutionStatus | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.approver, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(ToolExecution).where(ToolExecution.organization_id == user.organization_id)
    if status:
        statement = statement.where(ToolExecution.status == status)
    return session.exec(statement.order_by(ToolExecution.created_at.desc()).offset(skip).limit(limit)).all()


@router.get("/{execution_id}", response_model=ToolExecutionOut)
def get_execution(
    execution_id: int,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.approver, Role.auditor)),
    session: Session = Depends(get_session),
):
    execution = session.get(ToolExecution, execution_id)
    if not execution or execution.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/{execution_id}/retry", response_model=ToolExecutionOut)
def retry_execution(
    execution_id: int,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    execution = session.get(ToolExecution, execution_id)
    if not execution or execution.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status != ExecutionStatus.failed:
        raise HTTPException(status_code=409, detail="Only failed executions can be retried")
    from ..config import get_settings
    if execution.attempt_count >= get_settings().max_execution_attempts:
        raise HTTPException(status_code=409, detail="Execution retry limit reached")
    return run_execution(session, execution, user)
