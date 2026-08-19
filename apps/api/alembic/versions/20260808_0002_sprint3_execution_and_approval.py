"""Sprint 3 governed execution and approval lifecycle.

Revision ID: 20260808_0002
Revises: 20260727_0001
Create Date: 2026-08-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260808_0002"
down_revision: Union[str, None] = "20260727_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("approval") as batch_op:
        batch_op.add_column(sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index("ix_approval_expires_at", ["expires_at"], unique=False)

    # Backfill existing approvals before making updated_at required.
    op.execute("UPDATE approval SET updated_at = created_at WHERE updated_at IS NULL")
    with op.batch_alter_table("approval") as batch_op:
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)

    op.create_table(
        "toolexecution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=100), nullable=False),
        sa.Column("action_request_id", sa.Integer(), nullable=False),
        sa.Column("tool_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("tool_name", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=96), nullable=False),
        sa.Column("request_arguments", sa.JSON(), nullable=False),
        sa.Column("response_data", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.String(length=2000), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("initiated_by_email", sa.String(length=255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["action_request_id"], ["actionrequest.id"]),
        sa.ForeignKeyConstraint(["tool_id"], ["tool.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_execution_idempotency_key"),
    )
    op.create_index("ix_toolexecution_organization_id", "toolexecution", ["organization_id"])
    op.create_index("ix_toolexecution_action_request_id", "toolexecution", ["action_request_id"])
    op.create_index("ix_toolexecution_tool_id", "toolexecution", ["tool_id"])
    op.create_index("ix_toolexecution_provider", "toolexecution", ["provider"])
    op.create_index("ix_toolexecution_tool_name", "toolexecution", ["tool_name"])
    op.create_index("ix_toolexecution_status", "toolexecution", ["status"])
    op.create_index("ix_toolexecution_idempotency_key", "toolexecution", ["idempotency_key"])
    op.create_index("ix_execution_org_created", "toolexecution", ["organization_id", "created_at"])
    op.create_index("ix_execution_org_status", "toolexecution", ["organization_id", "status"])


def downgrade() -> None:
    op.drop_table("toolexecution")
    with op.batch_alter_table("approval") as batch_op:
        batch_op.drop_index("ix_approval_expires_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("expires_at")
