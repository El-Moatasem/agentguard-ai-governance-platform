from sqlmodel import Session
from ..models import AuditEvent, User


def write_audit_event(
    session: Session,
    *,
    user: User,
    event_type: str,
    result: str,
    message: str,
    metadata: dict | None = None,
    correlation_id: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        organization_id=user.organization_id,
        correlation_id=correlation_id,
        actor_email=user.email,
        event_type=event_type,
        result=result,
        message=message,
        event_metadata=metadata or {},
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
