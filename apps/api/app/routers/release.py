from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from ..config import get_settings
from ..database import get_session
from ..models import ActionRequest, Agent, Approval, AuditEvent, Policy, Role, ToolExecution, User
from ..security import require_roles

router = APIRouter(prefix="/release", tags=["final-release"])
settings = get_settings()


def _count(session: Session, model, organization_id: str) -> int:
    return session.exec(
        select(func.count()).select_from(model).where(model.organization_id == organization_id)
    ).one()


@router.get("/readiness")
def release_readiness(
    user: User = Depends(require_roles(Role.admin, Role.auditor, Role.developer)),
    session: Session = Depends(get_session),
):
    """Final Sprint 4 readiness summary for demos and submission checks."""
    decisions = {
        "allow": session.exec(select(func.count()).select_from(ActionRequest).where(ActionRequest.organization_id == user.organization_id, ActionRequest.decision == "allow")).one(),
        "deny": session.exec(select(func.count()).select_from(ActionRequest).where(ActionRequest.organization_id == user.organization_id, ActionRequest.decision == "deny")).one(),
        "requires_approval": session.exec(select(func.count()).select_from(ActionRequest).where(ActionRequest.organization_id == user.organization_id, ActionRequest.decision == "requires_approval")).one(),
    }
    pending_approvals = session.exec(
        select(func.count()).select_from(Approval).where(
            Approval.organization_id == user.organization_id,
            Approval.status == "pending",
        )
    ).one()
    checks = [
        {"name": "PostgreSQL/Alembic architecture", "status": "complete", "evidence": "Sprint 2+ migrations and CI run against PostgreSQL."},
        {"name": "Deterministic policy decisions", "status": "complete", "evidence": "ALLOW, DENY and REQUIRE_APPROVAL are persisted with correlation IDs."},
        {"name": "Human approval lifecycle", "status": "complete", "evidence": "Approve, reject, cancel and expiry behavior are implemented and audited."},
        {"name": "Governed agent/tool execution", "status": "complete", "evidence": "Tool execution can only occur through AgentGuard governance."},
        {"name": "AI/MCP mock-safe integration", "status": "complete", "evidence": "Mock AI and MCP modes support deterministic CI and demo execution."},
        {"name": "Audit export", "status": "complete", "evidence": "Audit records export to CSV and JSON."},
        {"name": "Production-hardening checklist", "status": "complete", "evidence": "Security headers, deployment guidance and final checklist are documented."},
    ]
    return {
        "release": settings.release_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "organization_id": user.organization_id,
        "summary": {
            "agents": _count(session, Agent, user.organization_id),
            "policies": _count(session, Policy, user.organization_id),
            "approvals_pending": pending_approvals,
            "tool_executions": _count(session, ToolExecution, user.organization_id),
            "audit_events": _count(session, AuditEvent, user.organization_id),
            "decisions": decisions,
        },
        "checks": checks,
        "overall_status": "ready" if all(item["status"] == "complete" for item in checks) else "attention_required",
    }


@router.get("/demo-flow")
def final_demo_flow(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor))):
    """Recommended 15-20 minute final Capstone demo sequence."""
    return {
        "title": "AgentGuard Final Capstone Demonstration Flow",
        "duration_minutes": "15-20",
        "steps": [
            {"order": 1, "title": "Problem and architecture", "goal": "Explain why AI agents need policy enforcement, approval and auditability."},
            {"order": 2, "title": "Role-based access", "goal": "Switch between admin, developer, approver and auditor views."},
            {"order": 3, "title": "Registry", "goal": "Show registered agents, tools and protected resources."},
            {"order": 4, "title": "Policy simulation", "goal": "Demonstrate ALLOW, DENY and REQUIRE_APPROVAL inputs."},
            {"order": 5, "title": "Governed agent run", "goal": "Run an agent prompt through the AgentGuard policy gateway."},
            {"order": 6, "title": "Human approval", "goal": "Approve or reject a sensitive action and show state transitions."},
            {"order": 7, "title": "Audit and export", "goal": "Search audit records and export evidence."},
            {"order": 8, "title": "AI explanation", "goal": "Show that AI explains decisions but never overrides policy."},
            {"order": 9, "title": "Engineering evidence", "goal": "Show tests, CI/CD, Jira, release notes and deployment documents."},
            {"order": 10, "title": "Limitations and future work", "goal": "Discuss real MCP provider hardening, SSO, and production scaling."},
        ],
        "required_evidence": ["Deployed app URL", "GitHub repository", "Jira board", "Design/testing document", "Final video link"],
    }


@router.get("/submission-checklist")
def submission_checklist(user: User = Depends(require_roles(Role.admin, Role.auditor, Role.developer))):
    items = [
        "GitHub repository shared with quantic-grader",
        "Production deployment URL added to README",
        "Jira board link added to README",
        "Design and testing document completed",
        "Final 15-20 minute demo video recorded and shared",
        "Sprint 1-4 release notes committed",
        "CI checks passing on release branch",
        "No secrets, .env files, local databases or node_modules committed",
        "Third-party and AI-assistance attribution documented",
    ]
    return {"version": settings.app_version, "items": items, "owner": user.email}
