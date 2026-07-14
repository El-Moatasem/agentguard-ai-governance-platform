from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import Policy, Role, User
from ..schemas import PolicyCreate
from ..security import require_roles

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("")
def list_policies(user: User = Depends(require_roles(Role.admin, Role.developer, Role.auditor)), session: Session = Depends(get_session)):
    return session.exec(select(Policy).where(Policy.organization_id == user.organization_id).order_by(Policy.priority.desc())).all()


@router.post("")
def create_policy(payload: PolicyCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    policy = Policy(organization_id=user.organization_id, **payload.model_dump())
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


@router.patch("/{policy_id}/deactivate")
def deactivate_policy(policy_id: int, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    policy = session.get(Policy, policy_id)
    if policy and policy.organization_id == user.organization_id:
        policy.active = False
        session.add(policy)
        session.commit()
        session.refresh(policy)
    return policy
