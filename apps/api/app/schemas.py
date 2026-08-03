from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from .models import PolicyEffect, ApprovalStatus

ALLOWED_POLICY_KEYS = {"agent_name", "user_email", "action", "resource_name", "environment"}
ALLOWED_OPERATORS = {"$eq", "$ne", "$in", "$not_in", "$gte", "$lte", "$gt", "$lt", "$contains"}


class LoginRequest(BaseModel):
    token: str = Field(examples=["admin-token"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AgentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    purpose: str = Field(min_length=5, max_length=1000)
    owner_email: str = Field(min_length=3, max_length=255)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    classification: str = Field(default="internal", pattern="^(public|internal|confidential|restricted)$")
    owner_team: str = Field(default="platform", min_length=2, max_length=150)


class ToolCreate(BaseModel):
    agent_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=150)
    endpoint: str = Field(min_length=1, max_length=500)
    allowed_actions: list[str] = Field(min_length=1)


class PolicyCreate(BaseModel):
    name: str = Field(min_length=3, max_length=180)
    description: str = Field(default="", max_length=2000)
    effect: PolicyEffect
    priority: int = Field(default=100, ge=0, le=10000)
    conditions: dict[str, Any] = Field(min_length=1)
    active: bool = True

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, value: dict[str, Any]) -> dict[str, Any]:
        for key, expected in value.items():
            if not (key in ALLOWED_POLICY_KEYS or key.startswith("context.")):
                raise ValueError(f"Unsupported policy condition key: {key}")
            if isinstance(expected, dict):
                unknown = set(expected) - ALLOWED_OPERATORS
                if unknown:
                    raise ValueError(f"Unsupported policy operators: {sorted(unknown)}")
        return value


class PolicyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=180)
    description: Optional[str] = Field(default=None, max_length=2000)
    effect: Optional[PolicyEffect] = None
    priority: Optional[int] = Field(default=None, ge=0, le=10000)
    conditions: Optional[dict[str, Any]] = None
    active: Optional[bool] = None
    change_summary: str = Field(default="Policy updated", max_length=500)

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, value: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if value is None:
            return value
        return PolicyCreate.validate_conditions(value)


class DecisionRequest(BaseModel):
    agent_name: str = Field(min_length=2, max_length=150)
    user_email: str = Field(min_length=3, max_length=255)
    action: str = Field(min_length=1, max_length=100)
    resource_name: str = Field(min_length=2, max_length=150)
    environment: str = Field(default="sandbox", pattern="^(sandbox|staging|production)$")
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyTestRequest(DecisionRequest):
    pass


class DecisionResponse(BaseModel):
    correlation_id: str
    decision: str
    reason: str
    matched_policy_id: Optional[int] = None
    matched_policy_name: Optional[str] = None
    evaluated_policy_count: int = 0
    action_request_id: Optional[int] = None
    approval_id: Optional[int] = None


class ActionRequestOut(BaseModel):
    id: int
    correlation_id: str
    agent_name: str
    user_email: str
    action: str
    resource_name: str
    environment: str
    context: dict[str, Any]
    decision: str
    reason: str
    matched_policy_id: Optional[int]
    evaluated_policy_count: int
    created_at: datetime


class ApprovalDecision(BaseModel):
    notes: str = Field(default="", max_length=2000)


class ApprovalOut(BaseModel):
    id: int
    action_request_id: int
    status: ApprovalStatus
    reviewer_email: Optional[str]
    reviewer_notes: str


class AssistantExplainRequest(BaseModel):
    action_request_id: int
