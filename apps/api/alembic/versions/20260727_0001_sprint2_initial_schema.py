"""Sprint 2 initial governance schema.

Revision ID: 20260727_0001
Revises: None
Create Date: 2026-07-27
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260727_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_user_org_email"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_is_active", "user", ["is_active"])
    op.create_index("ix_user_organization_id", "user", ["organization_id"])
    op.create_index("ix_user_role", "user", ["role"])
    op.create_index("ix_user_token", "user", ["token"])

    op.create_table(
        "agent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("purpose", sa.String(length=1000), nullable=False),
        sa.Column("owner_email", sa.String(length=255), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_agent_org_name"),
    )
    op.create_index("ix_agent_name", "agent", ["name"])
    op.create_index("ix_agent_organization_id", "agent", ["organization_id"])
    op.create_index("ix_agent_org_status", "agent", ["organization_id", "status"])

    op.create_table(
        "protectedresource",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("owner_team", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_resource_org_name"),
    )
    op.create_index("ix_protectedresource_name", "protectedresource", ["name"])
    op.create_index("ix_protectedresource_organization_id", "protectedresource", ["organization_id"])

    op.create_table(
        "policy",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("effect", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_by_email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_policy_org_name"),
    )
    op.create_index("ix_policy_active", "policy", ["active"])
    op.create_index("ix_policy_effect", "policy", ["effect"])
    op.create_index("ix_policy_organization_id", "policy", ["organization_id"])
    op.create_index("ix_policy_org_active_priority", "policy", ["organization_id", "active", "priority"])

    op.create_table(
        "tool",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("endpoint", sa.String(length=500), nullable=False),
        sa.Column("allowed_actions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "agent_id", "name", name="uq_tool_agent_name"),
    )
    op.create_index("ix_tool_agent_id", "tool", ["agent_id"])
    op.create_index("ix_tool_organization_id", "tool", ["organization_id"])

    op.create_table(
        "policyversion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("policy_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("effect", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("changed_by_email", sa.String(length=255), nullable=False),
        sa.Column("change_summary", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["policy_id"], ["policy.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("policy_id", "version", name="uq_policy_version"),
    )
    op.create_index("ix_policyversion_organization_id", "policyversion", ["organization_id"])
    op.create_index("ix_policyversion_policy_id", "policyversion", ["policy_id"])

    op.create_table(
        "actionrequest",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("agent_name", sa.String(length=150), nullable=False),
        sa.Column("user_email", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_name", sa.String(length=150), nullable=False),
        sa.Column("environment", sa.String(length=32), nullable=False),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=2000), nullable=False),
        sa.Column("matched_policy_id", sa.Integer(), nullable=True),
        sa.Column("evaluated_policy_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["matched_policy_id"], ["policy.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correlation_id"),
    )
    op.create_index("ix_actionrequest_action", "actionrequest", ["action"])
    op.create_index("ix_actionrequest_agent_name", "actionrequest", ["agent_name"])
    op.create_index("ix_actionrequest_correlation_id", "actionrequest", ["correlation_id"])
    op.create_index("ix_actionrequest_decision", "actionrequest", ["decision"])
    op.create_index("ix_actionrequest_matched_policy_id", "actionrequest", ["matched_policy_id"])
    op.create_index("ix_actionrequest_organization_id", "actionrequest", ["organization_id"])
    op.create_index("ix_actionrequest_resource_name", "actionrequest", ["resource_name"])
    op.create_index("ix_action_request_org_created", "actionrequest", ["organization_id", "created_at"])
    op.create_index("ix_action_request_org_decision", "actionrequest", ["organization_id", "decision"])

    op.create_table(
        "approval",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("action_request_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewer_email", sa.String(length=255), nullable=True),
        sa.Column("reviewer_notes", sa.String(length=2000), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["action_request_id"], ["actionrequest.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("action_request_id", name="uq_approval_action_request"),
    )
    op.create_index("ix_approval_action_request_id", "approval", ["action_request_id"])
    op.create_index("ix_approval_organization_id", "approval", ["organization_id"])
    op.create_index("ix_approval_status", "approval", ["status"])

    op.create_table(
        "auditevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("result", sa.String(length=100), nullable=False),
        sa.Column("message", sa.String(length=2000), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auditevent_actor_email", "auditevent", ["actor_email"])
    op.create_index("ix_auditevent_correlation_id", "auditevent", ["correlation_id"])
    op.create_index("ix_auditevent_event_type", "auditevent", ["event_type"])
    op.create_index("ix_auditevent_organization_id", "auditevent", ["organization_id"])
    op.create_index("ix_auditevent_result", "auditevent", ["result"])
    op.create_index("ix_audit_org_created", "auditevent", ["organization_id", "created_at"])
    op.create_index("ix_audit_org_type_result", "auditevent", ["organization_id", "event_type", "result"])


def downgrade() -> None:
    op.drop_table("auditevent")
    op.drop_table("approval")
    op.drop_table("actionrequest")
    op.drop_table("policyversion")
    op.drop_table("tool")
    op.drop_table("policy")
    op.drop_table("protectedresource")
    op.drop_table("agent")
    op.drop_table("user")
