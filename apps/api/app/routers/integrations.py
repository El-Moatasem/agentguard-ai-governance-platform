from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..config import get_settings
from ..database import get_session
from ..models import Role, Tool, User
from ..security import require_roles
from ..services.tool_execution import list_remote_mcp_tools

router = APIRouter(prefix="/integrations", tags=["integrations"])
settings = get_settings()


@router.get("/mcp/status")
def mcp_status(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor))):
    return {
        "mode": "mock" if settings.mcp_mock_mode or not settings.mcp_server_url else "remote",
        "configured": bool(settings.mcp_server_url),
        "authenticated": bool(settings.mcp_auth_token),
        "server": "configured" if settings.mcp_server_url else "not-configured",
    }


@router.get("/mcp/tools")
def list_mcp_tools(
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    registered = [
        tool for tool in session.exec(select(Tool).where(Tool.organization_id == user.organization_id)).all()
        if tool.endpoint.startswith("mcp://")
    ]
    mode = "mock" if settings.mcp_mock_mode or not settings.mcp_server_url else "remote"
    remote_by_name: dict[str, dict] = {}
    if mode == "remote":
        try:
            remote_by_name = {item["name"]: item for item in list_remote_mcp_tools()}
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    result = []
    for tool in registered:
        external_name = tool.endpoint.removeprefix("mcp://")
        if mode == "remote" and external_name not in remote_by_name:
            continue
        result.append({
            "id": tool.id,
            "name": tool.name,
            "external_name": external_name,
            "allowed_actions": tool.allowed_actions,
            "mode": mode,
            "remote_schema": remote_by_name.get(external_name, {}).get("inputSchema") if remote_by_name else None,
        })
    return result
