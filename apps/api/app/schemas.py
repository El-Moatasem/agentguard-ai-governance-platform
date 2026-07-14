from typing import Any, Optional
from pydantic import BaseModel, Field
from .models import PolicyEffect, ApprovalStatus


class LoginRequest(BaseModel):
    token: str = Field(examples=["admin-token"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AgentCreate(BaseModel):
    name: str
    purpose: str
    owner_email: str
    risk_level: str = "medium"


class ResourceCreate(BaseModel):
    name: str
    classification: str = "internal"
    owner_team: str = "platform"


class ToolCreate(BaseModel):
    agent_id: int
    name: str
    endpoint: str
    allowed_actions: list[str]


class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    effect: PolicyEffect
    priority: int = 100
    conditions: dict[str, Any] = Field(default_factory=dict)


class DecisionRequest(BaseModel):
    agent_name: str
    user_email: str
    action: str
    resource_name: str
    environment: str = "sandbox"
    context: dict[str, Any] = Field(default_factory=dict)


class DecisionResponse(BaseModel):
    decision: str
    reason: str
    matched_policy_id: Optional[int] = None
    action_request_id: Optional[int] = None
    approval_id: Optional[int] = None


class ApprovalDecision(BaseModel):
    notes: str = ""


class ApprovalOut(BaseModel):
    id: int
    action_request_id: int
    status: ApprovalStatus
    reviewer_email: Optional[str]
    reviewer_notes: str


class AssistantExplainRequest(BaseModel):
    action_request_id: int
