from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Agent, Role, Tool, User
from ..schemas import AgentPlan, AgentPromptRequest, AgentRunResponse, ToolExecutionRequest
from ..security import require_roles
from ..services.ai_provider import propose_agent_plan
from ..services.audit import write_audit_event
from ..services.security_guardrails import validate_agent_prompt
from .executions import submit_governed_execution

router = APIRouter(prefix="/agent-runtime", tags=["agent-runtime"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(
    payload: AgentPromptRequest,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    validate_agent_prompt(payload.prompt)
    agent = session.exec(
        select(Agent).where(
            Agent.organization_id == user.organization_id,
            Agent.name == payload.agent_name,
            Agent.status == "active",
        )
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Active agent not found")
    tools = session.exec(select(Tool).where(Tool.organization_id == user.organization_id, Tool.agent_id == agent.id)).all()
    if not tools:
        raise HTTPException(status_code=409, detail="Agent has no registered tools")

    provider, plan = propose_agent_plan(agent.name, payload.prompt, tools)
    registered_tool_names = {tool.name for tool in tools}
    if plan.tool_name not in registered_tool_names:
        raise HTTPException(status_code=400, detail="AI provider proposed an unregistered tool")

    write_audit_event(
        session,
        user=user,
        event_type="agent_plan",
        result="planned",
        message=f"Agent '{agent.name}' proposed registered tool '{plan.tool_name}'.",
        metadata={"provider": provider, "tool_name": plan.tool_name, "action": plan.action, "resource_name": plan.resource_name},
    )

    governance = None
    if payload.auto_execute:
        governance = submit_governed_execution(
            ToolExecutionRequest(
                agent_name=agent.name,
                tool_name=plan.tool_name,
                action=plan.action,
                resource_name=plan.resource_name,
                environment=payload.environment,
                arguments=plan.arguments,
                context={**plan.context, "agent_provider": provider},
            ),
            user,
            session,
        )

    return AgentRunResponse(provider=provider, plan=AgentPlan.model_validate(plan), governance=governance)
