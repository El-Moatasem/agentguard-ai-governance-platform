from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..models import Agent, ProtectedResource, Role, Tool, User
from ..schemas import AgentCreate, ResourceCreate, ToolCreate
from ..security import require_roles
from ..services.audit import write_audit_event

router = APIRouter(tags=["registry"])


def _commit_or_conflict(session: Session, detail: str) -> None:
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail=detail) from exc


@router.get("/agents")
def list_agents(
    status: str | None = None,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(Agent).where(Agent.organization_id == user.organization_id)
    if status:
        statement = statement.where(Agent.status == status)
    return session.exec(statement.order_by(Agent.name)).all()


@router.post("/agents", status_code=201)
def create_agent(
    payload: AgentCreate,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    agent = Agent(organization_id=user.organization_id, **payload.model_dump())
    session.add(agent)
    _commit_or_conflict(session, "An agent with this name already exists in the organization")
    session.refresh(agent)
    write_audit_event(
        session,
        user=user,
        event_type="agent_created",
        result="success",
        message=f"Agent '{agent.name}' was registered.",
        metadata={"agent_id": agent.id, "risk_level": agent.risk_level},
    )
    return agent


@router.get("/resources")
def list_resources(
    classification: str | None = None,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(ProtectedResource).where(ProtectedResource.organization_id == user.organization_id)
    if classification:
        statement = statement.where(ProtectedResource.classification == classification)
    return session.exec(statement.order_by(ProtectedResource.name)).all()


@router.post("/resources", status_code=201)
def create_resource(
    payload: ResourceCreate,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    resource = ProtectedResource(organization_id=user.organization_id, **payload.model_dump())
    session.add(resource)
    _commit_or_conflict(session, "A protected resource with this name already exists")
    session.refresh(resource)
    write_audit_event(
        session,
        user=user,
        event_type="resource_created",
        result="success",
        message=f"Protected resource '{resource.name}' was registered.",
        metadata={"resource_id": resource.id, "classification": resource.classification},
    )
    return resource


@router.get("/tools")
def list_tools(
    agent_id: int | None = None,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(Tool).where(Tool.organization_id == user.organization_id)
    if agent_id is not None:
        statement = statement.where(Tool.agent_id == agent_id)
    return session.exec(statement.order_by(Tool.name)).all()


@router.post("/tools", status_code=201)
def create_tool(
    payload: ToolCreate,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    agent = session.get(Agent, payload.agent_id)
    if not agent or agent.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    tool = Tool(organization_id=user.organization_id, **payload.model_dump())
    session.add(tool)
    _commit_or_conflict(session, "A tool with this name is already registered for the agent")
    session.refresh(tool)
    write_audit_event(
        session,
        user=user,
        event_type="tool_created",
        result="success",
        message=f"Tool '{tool.name}' was registered for agent '{agent.name}'.",
        metadata={"tool_id": tool.id, "agent_id": agent.id},
    )
    return tool
