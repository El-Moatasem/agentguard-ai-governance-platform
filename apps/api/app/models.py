from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from sqlalchemy import Column, Enum as SAEnum, Index, JSON, String, UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, Enum):
    admin = "admin"
    developer = "developer"
    approver = "approver"
    auditor = "auditor"


class PolicyEffect(str, Enum):
    allow = "allow"
    deny = "deny"
    requires_approval = "requires_approval"


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class User(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_user_org_email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(default="demo-bank", index=True, max_length=100)
    name: str = Field(max_length=150)
    email: str = Field(index=True, max_length=255)
    role: Role = Field(sa_column=Column(SAEnum(Role, native_enum=False, length=32), nullable=False, index=True))
    token: str = Field(index=True, unique=True, max_length=255)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utcnow)


class Agent(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_agent_org_name"),
        Index("ix_agent_org_status", "organization_id", "status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    name: str = Field(index=True, max_length=150)
    purpose: str = Field(max_length=1000)
    owner_email: str = Field(max_length=255)
    risk_level: str = Field(default="medium", max_length=32)
    status: str = Field(default="active", max_length=32)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Tool(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("organization_id", "agent_id", "name", name="uq_tool_agent_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    agent_id: int = Field(foreign_key="agent.id", index=True)
    name: str = Field(max_length=150)
    endpoint: str = Field(max_length=500)
    allowed_actions: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)


class ProtectedResource(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_resource_org_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    name: str = Field(index=True, max_length=150)
    classification: str = Field(default="internal", max_length=32)
    owner_team: str = Field(default="platform", max_length=150)
    created_at: datetime = Field(default_factory=utcnow)


class Policy(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_policy_org_name"),
        Index("ix_policy_org_active_priority", "organization_id", "active", "priority"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    name: str = Field(max_length=180)
    description: str = Field(default="", max_length=2000)
    effect: PolicyEffect = Field(sa_column=Column(SAEnum(PolicyEffect, native_enum=False, length=32), nullable=False, index=True))
    priority: int = Field(default=100, ge=0, le=10000)
    active: bool = Field(default=True, index=True)
    conditions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    version: int = Field(default=1, ge=1)
    created_by_email: str = Field(default="system", max_length=255)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class PolicyVersion(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("policy_id", "version", name="uq_policy_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    policy_id: int = Field(foreign_key="policy.id", index=True)
    version: int = Field(ge=1)
    name: str = Field(max_length=180)
    description: str = Field(default="", max_length=2000)
    effect: PolicyEffect = Field(sa_column=Column(SAEnum(PolicyEffect, native_enum=False, length=32), nullable=False))
    priority: int = Field(default=100)
    active: bool = Field(default=True)
    conditions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    changed_by_email: str = Field(max_length=255)
    change_summary: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=utcnow)


class ActionRequest(SQLModel, table=True):
    __table_args__ = (
        Index("ix_action_request_org_created", "organization_id", "created_at"),
        Index("ix_action_request_org_decision", "organization_id", "decision"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    correlation_id: str = Field(index=True, unique=True, max_length=64)
    agent_name: str = Field(index=True, max_length=150)
    user_email: str = Field(max_length=255)
    action: str = Field(index=True, max_length=100)
    resource_name: str = Field(index=True, max_length=150)
    environment: str = Field(default="sandbox", max_length=32)
    context: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    decision: str = Field(index=True, max_length=32)
    reason: str = Field(max_length=2000)
    matched_policy_id: Optional[int] = Field(default=None, foreign_key="policy.id", index=True)
    evaluated_policy_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utcnow)


class Approval(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("action_request_id", name="uq_approval_action_request"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    action_request_id: int = Field(foreign_key="actionrequest.id", index=True)
    status: ApprovalStatus = Field(sa_column=Column(SAEnum(ApprovalStatus, native_enum=False, length=32), nullable=False, index=True))
    reviewer_email: Optional[str] = Field(default=None, max_length=255)
    reviewer_notes: str = Field(default="", max_length=2000)
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)


class AuditEvent(SQLModel, table=True):
    __table_args__ = (
        Index("ix_audit_org_created", "organization_id", "created_at"),
        Index("ix_audit_org_type_result", "organization_id", "event_type", "result"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank", max_length=100)
    correlation_id: Optional[str] = Field(default=None, index=True, max_length=64)
    actor_email: str = Field(index=True, max_length=255)
    event_type: str = Field(index=True, max_length=100)
    result: str = Field(index=True, max_length=100)
    message: str = Field(max_length=2000)
    event_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)
