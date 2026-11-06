"""Incoming appointment events: envelope (report section 6.5) and what each one does to queues."""
import enum
import re
import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: uuid.UUID
    event_type: str
    event_version: int = 1
    aggregate_id: uuid.UUID  # the appointment ID
    aggregate_version: int
    occurred_at: datetime
    correlation_id: str | None = None
    producer: str | None = None
    payload: dict = {}


class AppointmentPayload(BaseModel):
    """Payload of appointment.booked and appointment.rescheduled (new date/time)."""

    model_config = ConfigDict(extra="ignore")

    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    appointment_date: date
    start_time: time
    end_time: time | None = None
    facility_id: uuid.UUID | None = None
    resource_id: uuid.UUID | None = None  # set when the appointment also uses a room/equipment


class Action(str, enum.Enum):
    BOOK = "book"
    RESCHEDULE = "reschedule"
    REMOVE = "remove"
    CHECK_IN = "check_in"
    COMPLETE = "complete"


NEEDS_PAYLOAD = (Action.BOOK, Action.RESCHEDULE)

# Suffix after "appointment." -> effect on the queue
_ACTIONS = {
    "booked": Action.BOOK,
    "rescheduled": Action.RESCHEDULE,
    "cancelled": Action.REMOVE,
    "auto_cancelled_late": Action.REMOVE,
    "cancelled_doctor_absent": Action.REMOVE,
    "no_show": Action.REMOVE,
    "expired": Action.REMOVE,
    "checked_in": Action.CHECK_IN,
    "completed": Action.COMPLETE,
}


def event_action(routing_key: str | None, event_type: str | None) -> Action | None:
    """Uses the routing key (appointment.booked), or else the event type (AppointmentBooked).
    Returns None for events this service does not care about."""
    name = None
    if routing_key and routing_key.startswith("appointment."):
        name = routing_key.split(".", 1)[1]
    elif event_type and (m := re.fullmatch(r"Appointment([A-Za-z]+)", event_type)):
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", m.group(1)).lower()
    return _ACTIONS.get(name) if name else None
