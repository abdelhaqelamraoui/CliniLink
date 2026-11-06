import uuid

from sqlalchemy import select

from app.consumer import Outcome, process_message
from app.db import SessionLocal
from app.models import EntryStatus, Queue, QueueEntry, QueueType
from tests.conftest import DAY, booked, event


async def entries_of(appointment_id):
    async with SessionLocal() as s:
        rows = await s.execute(select(QueueEntry, Queue).join(Queue).where(QueueEntry.appointment_id == appointment_id))
        return [(e.status, q.type, q.owner_id, str(q.date)) for e, q in rows.all()]


async def test_booking_adds_patient_to_doctor_and_resource_queues():
    appt, patient, doctor, room = (uuid.uuid4() for _ in range(4))
    outcome, keys = await process_message(*booked(appt, 1, patient, doctor, "10:00", resource_id=room))
    assert outcome == Outcome.ACK and len(keys) == 2
    assert sorted(await entries_of(appt)) == sorted([
        (EntryStatus.WAITING, QueueType.DOCTOR, doctor, DAY),
        (EntryStatus.WAITING, QueueType.RESOURCE, room, DAY),
    ])


async def test_same_event_delivered_twice_is_applied_once():
    appt, patient, doctor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    msg = booked(appt, 1, patient, doctor, "10:00", event_id=uuid.uuid4())
    assert (await process_message(*msg))[0] == Outcome.ACK
    assert (await process_message(*msg))[0] == Outcome.DUPLICATE
    assert len(await entries_of(appt)) == 1


async def test_cancellation_removes_entry():
    appt, patient, doctor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await process_message(*booked(appt, 1, patient, doctor, "10:00"))
    outcome, _ = await process_message(*event("cancelled", appt, 2))
    assert outcome == Outcome.ACK
    assert (await entries_of(appt))[0][0] == EntryStatus.REMOVED


async def test_out_of_order_events_keep_the_latest_state():
    """Cancellation (v2) arrives before the booking (v1): the patient must not appear in the queue."""
    appt, patient, doctor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await process_message(*event("cancelled", appt, 2))
    outcome, _ = await process_message(*booked(appt, 1, patient, doctor, "10:00"))
    assert outcome == Outcome.ACK
    assert await entries_of(appt) == []


async def test_reschedule_to_another_day_moves_the_entry():
    appt, patient, doctor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await process_message(*booked(appt, 1, patient, doctor, "10:00"))
    await process_message(*event("rescheduled", appt, 2, patient_id=patient, doctor_id=doctor,
                                 appointment_date="2026-11-12", start_time="09:00"))
    assert sorted(await entries_of(appt), key=lambda r: r[3]) == [
        (EntryStatus.REMOVED, QueueType.DOCTOR, doctor, DAY),
        (EntryStatus.WAITING, QueueType.DOCTOR, doctor, "2026-11-12"),
    ]


async def test_completed_marks_entry_done():
    appt, patient, doctor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    await process_message(*booked(appt, 1, patient, doctor, "10:00"))
    await process_message(*event("completed", appt, 2))
    assert (await entries_of(appt))[0][0] == EntryStatus.DONE


async def test_malformed_messages_are_rejected_to_dead_letter_queue():
    assert (await process_message(b"not json", "appointment.booked"))[0] == Outcome.REJECT
    # booked event missing doctor_id / date / time
    assert (await process_message(*event("booked", uuid.uuid4(), 1, patient_id=uuid.uuid4())))[0] == Outcome.REJECT


async def test_unrelated_event_is_acknowledged_without_changes():
    appt = uuid.uuid4()
    outcome, keys = await process_message(*event("payment_received", appt, 1))
    assert outcome == Outcome.ACK and keys == set()
