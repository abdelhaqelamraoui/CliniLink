import enum
import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Integer, String, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class QueueType(str, enum.Enum):
    DOCTOR = "DOCTOR"
    RESOURCE = "RESOURCE"


class EntryStatus(str, enum.Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    IN_CONSULTATION = "IN_CONSULTATION"
    DONE = "DONE"
    REMOVED = "REMOVED"


ACTIVE_STATUSES = (EntryStatus.WAITING, EntryStatus.CALLED, EntryStatus.IN_CONSULTATION)


class Queue(Base):
    """One queue per doctor (or resource) per day."""

    __tablename__ = "queues"
    __table_args__ = (UniqueConstraint("type", "owner_id", "date", name="uq_queue_owner_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[QueueType] = mapped_column(Enum(QueueType, name="queue_type"))
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))  # doctor_id or resource_id
    facility_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entries: Mapped[list["QueueEntry"]] = relationship(back_populates="queue", lazy="raise")


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    __table_args__ = (
        UniqueConstraint("queue_id", "appointment_id", name="uq_entry_queue_appointment"),
        Index("ix_queue_entries_queue_status", "queue_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("queues.id", ondelete="CASCADE"))
    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    scheduled_start: Mapped[time] = mapped_column(Time)
    scheduled_end: Mapped[time | None] = mapped_column(Time)
    status: Mapped[EntryStatus] = mapped_column(Enum(EntryStatus, name="queue_entry_status"))
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    queue: Mapped[Queue] = relationship(back_populates="entries", lazy="raise")


class AppointmentVersion(Base):
    """Last aggregate_version applied per appointment, to ignore out-of-order events."""

    __tablename__ = "appointment_versions"

    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    version: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProcessedEvent(Base):
    """Event IDs already handled, so redelivered messages are applied only once."""

    __tablename__ = "processed_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100))
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
