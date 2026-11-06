"""Queue business logic (QueueService in the class diagram)."""
import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth import Principal
from app.config import settings
from app.errors import ProblemError
from app.events import Action, AppointmentPayload, EventEnvelope
from app.models import ACTIVE_STATUSES, AppointmentVersion, EntryStatus, ProcessedEvent, Queue, QueueEntry, QueueType
from app.schemas import EntryView, MyQueueEntry, QueueSnapshot

log = logging.getLogger(__name__)
TZ = ZoneInfo(settings.timezone)

# Manual status changes allowed from the API (events can also move entries to DONE / REMOVED).
ALLOWED_TRANSITIONS: dict[EntryStatus, set[EntryStatus]] = {
    EntryStatus.WAITING: {EntryStatus.CALLED, EntryStatus.REMOVED},
    EntryStatus.CALLED: {EntryStatus.IN_CONSULTATION, EntryStatus.WAITING, EntryStatus.REMOVED},
    EntryStatus.IN_CONSULTATION: {EntryStatus.DONE},
    EntryStatus.DONE: set(),
    EntryStatus.REMOVED: set(),
}


@dataclass(frozen=True)
class QueueKey:
    """Identifies a queue without needing its row: (type, doctor/resource, day)."""

    type: QueueType
    owner_id: uuid.UUID
    date: date

    @property
    def channel(self) -> str:
        return f"{self.type.value}:{self.owner_id}:{self.date.isoformat()}"

    @classmethod
    def of(cls, q: Queue) -> "QueueKey":
        return cls(q.type, q.owner_id, q.date)


def today() -> date:
    return datetime.now(TZ).date()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------- events ----------

async def get_or_create_queue(s: AsyncSession, type_: QueueType, owner_id: uuid.UUID, day: date,
                              facility_id: uuid.UUID | None = None) -> Queue:
    await s.execute(
        pg_insert(Queue)
        .values(id=uuid.uuid4(), type=type_, owner_id=owner_id, date=day, facility_id=facility_id)
        .on_conflict_do_nothing(constraint="uq_queue_owner_date")
    )
    return (await s.execute(
        select(Queue).where(Queue.type == type_, Queue.owner_id == owner_id, Queue.date == day)
    )).scalar_one()


async def apply_event(s: AsyncSession, env: EventEnvelope, action: Action | None,
                      payload: AppointmentPayload | None) -> set[QueueKey] | None:
    """Applies one event inside the caller's transaction.
    Returns the queues that changed, or None if the event was already processed."""
    inserted = await s.execute(
        pg_insert(ProcessedEvent)
        .values(event_id=env.event_id, event_type=env.event_type)
        .on_conflict_do_nothing()
        .returning(ProcessedEvent.event_id)
    )
    if inserted.first() is None:
        log.info("Duplicate event %s ignored", env.event_id)
        return None
    if action is None:
        log.info("Event %s (%s) not relevant to queues", env.event_id, env.event_type)
        return set()

    appointment_id = env.aggregate_id
    # Lock the appointment's version row so concurrent events for it are applied one at a time.
    await s.execute(pg_insert(AppointmentVersion).values(appointment_id=appointment_id, version=0)
                    .on_conflict_do_nothing())
    av = (await s.execute(select(AppointmentVersion)
                          .where(AppointmentVersion.appointment_id == appointment_id)
                          .with_for_update())).scalar_one()
    if env.aggregate_version <= av.version:
        log.info("Stale event %s for appointment %s (version %s <= %s) ignored",
                 env.event_id, appointment_id, env.aggregate_version, av.version)
        return set()
    av.version = env.aggregate_version

    entries = list((await s.execute(
        select(QueueEntry).options(joinedload(QueueEntry.queue)).where(QueueEntry.appointment_id == appointment_id)
    )).scalars())
    affected = {QueueKey.of(e.queue) for e in entries}
    now = _now()

    if action in (Action.BOOK, Action.RESCHEDULE):
        assert payload is not None
        targets = [await get_or_create_queue(s, QueueType.DOCTOR, payload.doctor_id, payload.appointment_date,
                                             payload.facility_id)]
        if payload.resource_id:
            targets.append(await get_or_create_queue(s, QueueType.RESOURCE, payload.resource_id,
                                                     payload.appointment_date, payload.facility_id))
        by_queue = {e.queue_id: e for e in entries}
        for q in targets:
            entry = by_queue.get(q.id)
            if entry is None:
                s.add(QueueEntry(queue_id=q.id, appointment_id=appointment_id, patient_id=payload.patient_id,
                                 scheduled_start=payload.start_time, scheduled_end=payload.end_time,
                                 status=EntryStatus.WAITING, updated_at=now))
            else:
                entry.patient_id = payload.patient_id
                entry.scheduled_start, entry.scheduled_end = payload.start_time, payload.end_time
                if entry.status not in ACTIVE_STATUSES:
                    entry.status, entry.called_at, entry.checked_in_at = EntryStatus.WAITING, None, None
                entry.updated_at = now
            affected.add(QueueKey.of(q))
        # Rescheduled to another day / doctor / resource: leave the old queues.
        target_ids = {q.id for q in targets}
        for e in entries:
            if e.queue_id not in target_ids and e.status in ACTIVE_STATUSES:
                e.status, e.updated_at = EntryStatus.REMOVED, now

    elif action == Action.REMOVE:
        for e in entries:
            if e.status in ACTIVE_STATUSES:
                e.status, e.updated_at = EntryStatus.REMOVED, now

    elif action == Action.CHECK_IN:
        for e in entries:
            if e.status in ACTIVE_STATUSES and e.checked_in_at is None:
                e.checked_in_at, e.updated_at = env.occurred_at, now

    elif action == Action.COMPLETE:
        for e in entries:
            if e.status != EntryStatus.REMOVED:
                e.status, e.updated_at = EntryStatus.DONE, now

    await s.flush()
    return affected


# ---------- reads ----------

def _view(e: QueueEntry, position: int, day: date, full: bool, viewer: Principal | None) -> EntryView:
    v = EntryView(
        entry_id=e.id, position=position, status=e.status,
        scheduled_start=e.scheduled_start, scheduled_end=e.scheduled_end,
        estimated_time=datetime.combine(day, e.scheduled_start, tzinfo=TZ),
        checked_in=e.checked_in_at is not None,
    )
    if full:
        v.appointment_id, v.patient_id = e.appointment_id, e.patient_id
    elif viewer is not None:
        v.is_mine = e.patient_id == viewer.user_id
    return v


async def _active_entries(s: AsyncSession, queue_id: uuid.UUID) -> list[QueueEntry]:
    return list((await s.execute(
        select(QueueEntry)
        .where(QueueEntry.queue_id == queue_id, QueueEntry.status.in_(ACTIVE_STATUSES))
        .order_by(QueueEntry.scheduled_start, QueueEntry.created_at, QueueEntry.id)
    )).scalars())


async def build_snapshot(s: AsyncSession, key: QueueKey, viewer: Principal | None = None) -> QueueSnapshot:
    """viewer=None gives the public view (waiting-room screens, WebSocket): no patient data."""
    q = (await s.execute(select(Queue).where(
        Queue.type == key.type, Queue.owner_id == key.owner_id, Queue.date == key.date))).scalar_one_or_none()
    entries = await _active_entries(s, q.id) if q else []
    full = viewer is not None and viewer.can_manage(key.type, key.owner_id)
    current = [_view(e, 0, key.date, full, viewer) for e in entries if e.status != EntryStatus.WAITING]
    waiting = [_view(e, i, key.date, full, viewer)
               for i, e in enumerate((e for e in entries if e.status == EntryStatus.WAITING), start=1)]
    return QueueSnapshot(
        queue_id=q.id if q else None, type=key.type,
        doctor_id=key.owner_id if key.type == QueueType.DOCTOR else None,
        resource_id=key.owner_id if key.type == QueueType.RESOURCE else None,
        facility_id=q.facility_id if q else None,
        date=key.date, waiting_count=len(waiting), current=current, waiting=waiting, updated_at=_now(),
    )


async def my_entries(s: AsyncSession, viewer: Principal) -> list[MyQueueEntry]:
    rows = (await s.execute(
        select(QueueEntry.queue_id).join(Queue)
        .where(QueueEntry.patient_id == viewer.user_id, QueueEntry.status.in_(ACTIVE_STATUSES),
               Queue.date >= today())
        .distinct()
    )).scalars().all()
    result = []
    for queue_id in rows:
        q = await s.get(Queue, queue_id)
        snap = await build_snapshot(s, QueueKey.of(q), viewer)
        for v in snap.current + snap.waiting:
            if v.is_mine or (v.patient_id == viewer.user_id):
                result.append(MyQueueEntry(queue_id=q.id, type=q.type, doctor_id=snap.doctor_id,
                                           resource_id=snap.resource_id, date=q.date, entry=v))
    return sorted(result, key=lambda m: (m.date, m.entry.scheduled_start))


# ---------- staff / doctor actions ----------

async def get_queue_for_manager(s: AsyncSession, queue_id: uuid.UUID, viewer: Principal) -> Queue:
    q = await s.get(Queue, queue_id)
    if q is None:
        raise ProblemError(404, "QUEUE_NOT_FOUND", "Queue Not Found", f"No queue with id {queue_id}.")
    if not viewer.can_manage(q.type, q.owner_id):
        raise ProblemError(403, "FORBIDDEN", "Forbidden", "You cannot manage this queue.")
    return q


async def call_next(s: AsyncSession, q: Queue) -> QueueEntry:
    # SKIP LOCKED: two staff members pressing "call next" at once call two different patients.
    entry = (await s.execute(
        select(QueueEntry)
        .where(QueueEntry.queue_id == q.id, QueueEntry.status == EntryStatus.WAITING)
        .order_by(QueueEntry.scheduled_start, QueueEntry.created_at, QueueEntry.id)
        .limit(1)
        .with_for_update(skip_locked=True)
    )).scalar_one_or_none()
    if entry is None:
        raise ProblemError(409, "QUEUE_EMPTY", "Queue Empty", "No patient is waiting in this queue.")
    entry.status, entry.called_at, entry.updated_at = EntryStatus.CALLED, _now(), _now()
    await s.flush()
    return entry


async def change_status(s: AsyncSession, q: Queue, entry_id: uuid.UUID, new_status: EntryStatus) -> QueueEntry:
    entry = (await s.execute(
        select(QueueEntry).where(QueueEntry.id == entry_id, QueueEntry.queue_id == q.id).with_for_update()
    )).scalar_one_or_none()
    if entry is None:
        raise ProblemError(404, "ENTRY_NOT_FOUND", "Entry Not Found", f"No entry {entry_id} in this queue.")
    if new_status not in ALLOWED_TRANSITIONS[entry.status]:
        raise ProblemError(409, "INVALID_TRANSITION", "Invalid Status Transition",
                           f"Cannot go from {entry.status.value} to {new_status.value}.")
    entry.status, entry.updated_at = new_status, _now()
    if new_status == EntryStatus.CALLED:
        entry.called_at = _now()
    await s.flush()
    return entry

