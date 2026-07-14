from datetime import datetime
from enum import Enum
from typing import Any, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


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
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = "demo-bank"
    name: str
    email: str = Field(index=True, unique=True)
    role: Role
    token: str = Field(index=True, unique=True)
    is_active: bool = True


class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    name: str = Field(index=True)
    purpose: str
    owner_email: str
    risk_level: str = "medium"
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Tool(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    agent_id: int = Field(index=True)
    name: str
    endpoint: str
    allowed_actions: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class ProtectedResource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    name: str = Field(index=True)
    classification: str = "internal"
    owner_team: str = "platform"


class Policy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    name: str
    description: str = ""
    effect: PolicyEffect
    priority: int = 100
    active: bool = True
    conditions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActionRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    agent_name: str
    user_email: str
    action: str
    resource_name: str
    environment: str = "sandbox"
    context: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    decision: str
    reason: str
    matched_policy_id: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Approval(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    action_request_id: int = Field(index=True)
    status: ApprovalStatus = ApprovalStatus.pending
    reviewer_email: Optional[str] = None
    reviewer_notes: str = ""
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: str = Field(index=True, default="demo-bank")
    actor_email: str
    event_type: str = Field(index=True)
    result: str = Field(index=True)
    message: str
    event_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
