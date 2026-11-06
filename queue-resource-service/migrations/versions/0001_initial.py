"""Initial schema: queues, queue entries, appointment versions, processed events.

Revision ID: 0001
Revises:
Create Date: 2026-11-06
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

QUEUE_TYPE = sa.Enum("DOCTOR", "RESOURCE", name="queue_type")
ENTRY_STATUS = sa.Enum("WAITING", "CALLED", "IN_CONSULTATION", "DONE", "REMOVED", name="queue_entry_status")


def upgrade() -> None:
    op.create_table(
        "queues",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("type", QUEUE_TYPE, nullable=False),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("facility_id", UUID(as_uuid=True), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("type", "owner_id", "date", name="uq_queue_owner_date"),
    )
    op.create_table(
        "queue_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("queue_id", UUID(as_uuid=True), sa.ForeignKey("queues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appointment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("patient_id", UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_start", sa.Time(), nullable=False),
        sa.Column("scheduled_end", sa.Time(), nullable=True),
        sa.Column("status", ENTRY_STATUS, nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("queue_id", "appointment_id", name="uq_entry_queue_appointment"),
    )
    op.create_index("ix_queue_entries_appointment_id", "queue_entries", ["appointment_id"])
    op.create_index("ix_queue_entries_patient_id", "queue_entries", ["patient_id"])
    op.create_index("ix_queue_entries_queue_status", "queue_entries", ["queue_id", "status"])
    op.create_table(
        "appointment_versions",
        sa.Column("appointment_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "processed_events",
        sa.Column("event_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("processed_events")
    op.drop_table("appointment_versions")
    op.drop_table("queue_entries")
    op.drop_table("queues")
    ENTRY_STATUS.drop(op.get_bind(), checkfirst=True)
    QUEUE_TYPE.drop(op.get_bind(), checkfirst=True)
