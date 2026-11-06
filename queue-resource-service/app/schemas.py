import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, model_serializer

from app.models import EntryStatus, QueueType


class EntryView(BaseModel):
    entry_id: uuid.UUID
    position: int  # 0 = being served (CALLED / IN_CONSULTATION), 1 = next, ...
    status: EntryStatus
    scheduled_start: time
    scheduled_end: time | None = None
    estimated_time: datetime
    checked_in: bool
    # Only for the queue's doctor and staff:
    appointment_id: uuid.UUID | None = None
    patient_id: uuid.UUID | None = None
    # Only for patients: marks their own entry
    is_mine: bool | None = None

    @model_serializer(mode="wrap")
    def _hide_unset_viewer_fields(self, handler):
        data = handler(self)
        for k in ("appointment_id", "patient_id", "is_mine"):
            if data.get(k) is None:
                data.pop(k, None)
        return data


class QueueSnapshot(BaseModel):
    queue_id: uuid.UUID | None  # None when nobody is booked on that day yet
    type: QueueType
    doctor_id: uuid.UUID | None = None
    resource_id: uuid.UUID | None = None
    facility_id: uuid.UUID | None = None
    date: date
    waiting_count: int
    current: list[EntryView]
    waiting: list[EntryView]
    updated_at: datetime


class MyQueueEntry(BaseModel):
    queue_id: uuid.UUID
    type: QueueType
    doctor_id: uuid.UUID | None = None
    resource_id: uuid.UUID | None = None
    date: date
    entry: EntryView


class StatusUpdate(BaseModel):
    status: EntryStatus


class CallNextResult(BaseModel):
    called: EntryView
    queue: QueueSnapshot
