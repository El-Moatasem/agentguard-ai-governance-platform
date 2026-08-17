import csv
import io
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, func, select
from ..database import get_session
from ..models import ActionRequest, Agent, Approval, AuditEvent, Policy, Role, ToolExecution, User
from ..security import require_roles

router = APIRouter(tags=["audit"])


def _audit_statement(user: User, *, event_type: str | None, result: str | None, actor_email: str | None, correlation_id: str | None):
    statement = select(AuditEvent).where(AuditEvent.organization_id == user.organization_id)
    if event_type:
        statement = statement.where(AuditEvent.event_type == event_type)
    if result:
        statement = statement.where(AuditEvent.result == result)
    if actor_email:
        statement = statement.where(AuditEvent.actor_email == actor_email)
    if correlation_id:
        statement = statement.where(AuditEvent.correlation_id == correlation_id)
    return statement


@router.get("/audit-events")
def list_audit_events(
    event_type: str | None = None,
    result: str | None = None,
    actor_email: str | None = None,
    correlation_id: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    user: User = Depends(require_roles(Role.admin, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = _audit_statement(
        user,
        event_type=event_type,
        result=result,
        actor_email=actor_email,
        correlation_id=correlation_id,
    )
    return session.exec(statement.order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit)).all()


@router.get("/audit-events/export")
def export_audit_events(
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    event_type: str | None = None,
    result: str | None = None,
    actor_email: str | None = None,
    correlation_id: str | None = None,
    user: User = Depends(require_roles(Role.admin, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = _audit_statement(
        user,
        event_type=event_type,
        result=result,
        actor_email=actor_email,
        correlation_id=correlation_id,
    ).order_by(AuditEvent.created_at.desc())
    events = session.exec(statement).all()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if format == "json":
        payload = [event.model_dump(mode="json") for event in events]
        content = json.dumps(payload, indent=2)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=agentguard-audit-{timestamp}.json"},
        )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "created_at", "correlation_id", "actor_email", "event_type", "result", "message", "metadata"])
    for event in events:
        writer.writerow([
            event.id,
            event.created_at.isoformat(),
            event.correlation_id or "",
            event.actor_email,
            event.event_type,
            event.result,
            event.message,
            json.dumps(event.event_metadata, sort_keys=True),
        ])
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=agentguard-audit-{timestamp}.csv"},
    )


@router.get("/dashboard/metrics")
def dashboard_metrics(
    user: User = Depends(require_roles(Role.admin, Role.auditor, Role.developer)),
    session: Session = Depends(get_session),
):
    def count(model):
        return session.exec(select(func.count()).select_from(model).where(model.organization_id == user.organization_id)).one()

    def count_decisions(result: str):
        return session.exec(
            select(func.count()).select_from(ActionRequest).where(
                ActionRequest.organization_id == user.organization_id,
                ActionRequest.decision == result,
            )
        ).one()

    pending = session.exec(
        select(func.count()).select_from(Approval).where(
            Approval.organization_id == user.organization_id,
            Approval.status == "pending",
        )
    ).one()
    active_policies = session.exec(
        select(func.count()).select_from(Policy).where(
            Policy.organization_id == user.organization_id,
            Policy.active == True,
        )
    ).one()
    return {
        "agents": count(Agent),
        "policies": count(Policy),
        "active_policies": active_policies,
        "audit_events": count(AuditEvent),
        "pending_approvals": pending,
        "tool_executions": count(ToolExecution),
        "decisions": {
            "allow": count_decisions("allow"),
            "deny": count_decisions("deny"),
            "requires_approval": count_decisions("requires_approval"),
        },
    }
