from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..config import get_settings
from ..models import ActionRequest, ExecutionStatus, Tool, ToolExecution, User, utcnow
from .audit import write_audit_event
from .security_guardrails import redact_sensitive, validate_tool_arguments

settings = get_settings()


@dataclass
class AdapterResult:
    provider: str
    data: dict[str, Any]


def provider_for_tool(tool: Tool) -> str:
    if tool.endpoint.startswith("mcp://"):
        return "mcp"
    return "mock"


def _mock_execute(tool: Tool, arguments: dict[str, Any], idempotency_key: str) -> AdapterResult:
    external_name = tool.endpoint.removeprefix("mock://") or tool.name
    return AdapterResult(
        provider="mock",
        data={
            "ok": True,
            "tool": external_name,
            "idempotency_key": idempotency_key,
            "echo": redact_sensitive(arguments),
        },
    )


def _mcp_execute(tool: Tool, arguments: dict[str, Any], idempotency_key: str) -> AdapterResult:
    external_name = tool.endpoint.removeprefix("mcp://")
    if settings.mcp_mock_mode or not settings.mcp_server_url:
        return AdapterResult(
            provider="mcp-mock",
            data={
                "ok": True,
                "tool": external_name,
                "idempotency_key": idempotency_key,
                "content": [{"type": "text", "text": f"Mock MCP call completed for {external_name}."}],
                "arguments": redact_sensitive(arguments),
            },
        )

    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if settings.mcp_auth_token:
        headers["Authorization"] = f"Bearer {settings.mcp_auth_token}"
    payload = {
        "jsonrpc": "2.0",
        "id": idempotency_key,
        "method": "tools/call",
        "params": {"name": external_name, "arguments": arguments},
    }
    try:
        with httpx.Client(timeout=settings.tool_timeout_seconds) as client:
            response = client.post(settings.mcp_server_url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(f"MCP provider call failed: {exc}") from exc
    if body.get("error"):
        raise RuntimeError(f"MCP provider returned an error: {body['error']}")
    return AdapterResult(provider="mcp", data=body.get("result", body))


def list_remote_mcp_tools() -> list[dict[str, Any]]:
    """Return remote MCP tool descriptors when configured.

    The integration router intersects this list with locally registered mcp:// tools,
    so remote discovery never expands AgentGuard's allowlist.
    """
    if settings.mcp_mock_mode or not settings.mcp_server_url:
        return []
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if settings.mcp_auth_token:
        headers["Authorization"] = f"Bearer {settings.mcp_auth_token}"
    payload = {"jsonrpc": "2.0", "id": "agentguard-tools-list", "method": "tools/list", "params": {}}
    try:
        with httpx.Client(timeout=settings.tool_timeout_seconds) as client:
            response = client.post(settings.mcp_server_url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(f"MCP tools/list failed: {exc}") from exc
    if body.get("error"):
        raise RuntimeError(f"MCP provider returned an error: {body['error']}")
    result = body.get("result", {})
    tools = result.get("tools", []) if isinstance(result, dict) else []
    return [tool for tool in tools if isinstance(tool, dict) and isinstance(tool.get("name"), str)]


def execute_tool(tool: Tool, arguments: dict[str, Any], idempotency_key: str) -> AdapterResult:
    validate_tool_arguments(arguments)
    if tool.endpoint.startswith("mcp://"):
        return _mcp_execute(tool, arguments, idempotency_key)
    return _mock_execute(tool, arguments, idempotency_key)


def create_execution(
    session: Session,
    *,
    action_request: ActionRequest,
    tool: Tool,
    user: User,
    arguments: dict[str, Any],
    status: ExecutionStatus,
    idempotency_key: str | None = None,
) -> ToolExecution:
    key = idempotency_key or f"ag-{uuid4().hex}"
    existing = session.exec(select(ToolExecution).where(ToolExecution.idempotency_key == key)).first()
    if existing:
        if existing.organization_id != user.organization_id:
            raise HTTPException(status_code=409, detail="Idempotency key is already in use")
        return existing

    execution = ToolExecution(
        organization_id=user.organization_id,
        action_request_id=action_request.id,
        tool_id=tool.id,
        provider=provider_for_tool(tool),
        tool_name=tool.name,
        status=status,
        idempotency_key=key,
        request_arguments=redact_sensitive(arguments),
        initiated_by_email=user.email,
    )
    session.add(execution)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        existing = session.exec(select(ToolExecution).where(ToolExecution.idempotency_key == key)).first()
        if existing:
            return existing
        raise HTTPException(status_code=409, detail="Execution idempotency conflict") from exc
    session.refresh(execution)
    return execution


def run_execution(session: Session, execution: ToolExecution, user: User) -> ToolExecution:
    if execution.status == ExecutionStatus.succeeded:
        return execution
    if execution.status in {ExecutionStatus.blocked, ExecutionStatus.cancelled}:
        raise HTTPException(status_code=409, detail=f"Execution is {execution.status.value}")

    tool = session.get(Tool, execution.tool_id)
    action_request = session.get(ActionRequest, execution.action_request_id)
    if not tool or tool.organization_id != user.organization_id or not action_request:
        raise HTTPException(status_code=404, detail="Execution dependencies not found")

    execution.status = ExecutionStatus.running
    execution.attempt_count += 1
    execution.started_at = utcnow()
    execution.updated_at = utcnow()
    session.add(execution)
    session.commit()

    try:
        result = execute_tool(tool, execution.request_arguments, execution.idempotency_key)
        execution.provider = result.provider
        execution.response_data = redact_sensitive(result.data)
        execution.error_message = ""
        execution.status = ExecutionStatus.succeeded
        audit_result = "succeeded"
        audit_message = f"Governed tool execution {execution.id} completed successfully."
    except Exception as exc:  # provider failures are converted into an auditable execution state
        execution.response_data = {}
        execution.error_message = str(exc)[:2000]
        execution.status = ExecutionStatus.failed
        audit_result = "failed"
        audit_message = f"Governed tool execution {execution.id} failed."

    execution.completed_at = utcnow()
    execution.updated_at = utcnow()
    session.add(execution)
    session.commit()
    session.refresh(execution)

    write_audit_event(
        session,
        user=user,
        event_type="tool_execution",
        result=audit_result,
        message=audit_message,
        correlation_id=action_request.correlation_id,
        metadata={
            "execution_id": execution.id,
            "action_request_id": action_request.id,
            "tool_id": tool.id,
            "tool_name": tool.name,
            "provider": execution.provider,
            "attempt_count": execution.attempt_count,
        },
    )
    return execution
