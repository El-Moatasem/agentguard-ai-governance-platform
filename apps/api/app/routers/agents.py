from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import Agent, ProtectedResource, Role, Tool, User
from ..schemas import AgentCreate, ResourceCreate, ToolCreate
from ..security import require_roles

router = APIRouter(tags=["registry"])


@router.get("/agents")
def list_agents(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(Agent).where(Agent.organization_id == user.organization_id)).all()


@router.post("/agents")
def create_agent(payload: AgentCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    agent = Agent(organization_id=user.organization_id, **payload.model_dump())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.get("/resources")
def list_resources(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(ProtectedResource).where(ProtectedResource.organization_id == user.organization_id)).all()


@router.post("/resources")
def create_resource(payload: ResourceCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    resource = ProtectedResource(organization_id=user.organization_id, **payload.model_dump())
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource


@router.get("/tools")
def list_tools(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(Tool).where(Tool.organization_id == user.organization_id)).all()


@router.post("/tools")
def create_tool(payload: ToolCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    tool = Tool(organization_id=user.organization_id, **payload.model_dump())
    session.add(tool)
    session.commit()
    session.refresh(tool)
    return tool
