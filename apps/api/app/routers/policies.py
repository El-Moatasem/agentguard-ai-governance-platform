from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ..database import get_session
from ..models import Policy, PolicyEffect, PolicyVersion, Role, User
from ..schemas import DecisionResponse, PolicyCreate, PolicyTestRequest, PolicyUpdate
from ..security import require_roles
from ..services.audit import write_audit_event
from ..services.policy_engine import PolicyEngine

router = APIRouter(prefix="/policies", tags=["policies"])
engine = PolicyEngine()


def _snapshot(session: Session, policy: Policy, changed_by: str, summary: str) -> PolicyVersion:
    version = PolicyVersion(
        organization_id=policy.organization_id,
        policy_id=policy.id,
        version=policy.version,
        name=policy.name,
        description=policy.description,
        effect=policy.effect,
        priority=policy.priority,
        active=policy.active,
        conditions=policy.conditions,
        changed_by_email=changed_by,
        change_summary=summary,
    )
    session.add(version)
    return version


def _get_policy_or_404(session: Session, policy_id: int, organization_id: str) -> Policy:
    policy = session.get(Policy, policy_id)
    if not policy or policy.organization_id != organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.get("")
def list_policies(
    active: bool | None = None,
    effect: PolicyEffect | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    statement = select(Policy).where(Policy.organization_id == user.organization_id)
    if active is not None:
        statement = statement.where(Policy.active == active)
    if effect is not None:
        statement = statement.where(Policy.effect == effect.value)
    return session.exec(statement.order_by(Policy.priority.desc(), Policy.name).offset(skip).limit(limit)).all()


@router.get("/{policy_id}")
def get_policy(
    policy_id: int,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    return _get_policy_or_404(session, policy_id, user.organization_id)


@router.post("", status_code=201)
def create_policy(
    payload: PolicyCreate,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    policy = Policy(
        organization_id=user.organization_id,
        created_by_email=user.email,
        **payload.model_dump(),
    )
    session.add(policy)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="A policy with this name already exists") from exc
    session.refresh(policy)
    _snapshot(session, policy, user.email, "Initial policy version")
    session.commit()
    write_audit_event(
        session,
        user=user,
        event_type="policy_created",
        result="success",
        message=f"Policy '{policy.name}' was created.",
        metadata={"policy_id": policy.id, "version": policy.version, "effect": policy.effect},
    )
    return policy


@router.patch("/{policy_id}")
def update_policy(
    policy_id: int,
    payload: PolicyUpdate,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    policy = _get_policy_or_404(session, policy_id, user.organization_id)
    changes = payload.model_dump(exclude_unset=True, exclude={"change_summary"})
    if not changes:
        raise HTTPException(status_code=422, detail="At least one policy field must be changed")

    for field, value in changes.items():
        setattr(policy, field, value)
    policy.version += 1
    policy.updated_at = datetime.now(timezone.utc)
    session.add(policy)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Policy update conflicts with an existing policy") from exc
    session.refresh(policy)
    _snapshot(session, policy, user.email, payload.change_summary)
    session.commit()
    write_audit_event(
        session,
        user=user,
        event_type="policy_updated",
        result="success",
        message=f"Policy '{policy.name}' was updated to version {policy.version}.",
        metadata={"policy_id": policy.id, "version": policy.version, "changed_fields": sorted(changes)},
    )
    return policy


@router.get("/{policy_id}/versions")
def list_policy_versions(
    policy_id: int,
    user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)),
    session: Session = Depends(get_session),
):
    _get_policy_or_404(session, policy_id, user.organization_id)
    statement = (
        select(PolicyVersion)
        .where(PolicyVersion.organization_id == user.organization_id, PolicyVersion.policy_id == policy_id)
        .order_by(PolicyVersion.version.desc())
    )
    return session.exec(statement).all()


@router.post("/{policy_id}/activate")
def activate_policy(
    policy_id: int,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    return _set_active(policy_id, True, user, session)


@router.post("/{policy_id}/deactivate")
def deactivate_policy(
    policy_id: int,
    user: User = Depends(require_roles(Role.admin)),
    session: Session = Depends(get_session),
):
    return _set_active(policy_id, False, user, session)


def _set_active(policy_id: int, active: bool, user: User, session: Session):
    policy = _get_policy_or_404(session, policy_id, user.organization_id)
    if policy.active == active:
        return policy
    policy.active = active
    policy.version += 1
    policy.updated_at = datetime.now(timezone.utc)
    session.add(policy)
    session.commit()
    session.refresh(policy)
    _snapshot(session, policy, user.email, "Policy activated" if active else "Policy deactivated")
    session.commit()
    write_audit_event(
        session,
        user=user,
        event_type="policy_status_changed",
        result="active" if active else "inactive",
        message=f"Policy '{policy.name}' was {'activated' if active else 'deactivated'}.",
        metadata={"policy_id": policy.id, "version": policy.version},
    )
    return policy


@router.post("/test/evaluate", response_model=DecisionResponse)
def test_policies(
    payload: PolicyTestRequest,
    user: User = Depends(require_roles(Role.admin, Role.developer)),
    session: Session = Depends(get_session),
):
    policies = session.exec(select(Policy).where(Policy.organization_id == user.organization_id)).all()
    decision = engine.evaluate(policies=policies, request=payload.model_dump())
    return DecisionResponse(
        correlation_id="dry-run",
        decision=decision.decision,
        reason=decision.reason,
        matched_policy_id=decision.matched_policy_id,
        matched_policy_name=decision.matched_policy_name,
        evaluated_policy_count=decision.evaluated_policy_count,
    )
