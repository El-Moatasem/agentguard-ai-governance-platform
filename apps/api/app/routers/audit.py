from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select
from ..database import get_session
from ..models import Agent, Approval, AuditEvent, Policy, Role, User
from ..security import require_roles

router = APIRouter(tags=["audit"])


@router.get("/audit-events")
def list_audit_events(user: User = Depends(require_roles(Role.admin, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(AuditEvent).where(AuditEvent.organization_id == user.organization_id).order_by(AuditEvent.created_at.desc()).limit(100)).all()


@router.get("/dashboard/metrics")
def dashboard_metrics(user: User = Depends(require_roles(Role.admin, Role.auditor, Role.developer)), session: Session = Depends(get_session)):
    def count(model):
        return session.exec(select(func.count()).select_from(model).where(model.organization_id == user.organization_id)).one()

    pending = session.exec(select(func.count()).select_from(Approval).where(Approval.organization_id == user.organization_id, Approval.status == "pending")).one()
    return {
        "agents": count(Agent),
        "policies": count(Policy),
        "audit_events": count(AuditEvent),
        "pending_approvals": pending,
    }
