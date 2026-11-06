import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import Principal, current_principal
from app.db import get_session
from app.models import QueueType
from app.realtime import publish_snapshots
from app.schemas import CallNextResult, MyQueueEntry, QueueSnapshot, StatusUpdate
from app.service import QueueKey, build_snapshot, call_next, change_status, get_queue_for_manager, my_entries, today

router = APIRouter(prefix="/api/v1/queues", tags=["queues"])

DayParam = Query(default=None, alias="date", description="YYYY-MM-DD, defaults to today")


@router.get("/doctors/{doctor_id}", response_model=QueueSnapshot,
            summary="Current queue of a doctor (FR19)")
async def get_doctor_queue(doctor_id: uuid.UUID, day: date | None = DayParam,
                           viewer: Principal = Depends(current_principal),
                           s: AsyncSession = Depends(get_session)):
    return await build_snapshot(s, QueueKey(QueueType.DOCTOR, doctor_id, day or today()), viewer)


@router.get("/resources/{resource_id}", response_model=QueueSnapshot,
            summary="Current queue of a facility resource (FR20)")
async def get_resource_queue(resource_id: uuid.UUID, day: date | None = DayParam,
                             viewer: Principal = Depends(current_principal),
                             s: AsyncSession = Depends(get_session)):
    return await build_snapshot(s, QueueKey(QueueType.RESOURCE, resource_id, day or today()), viewer)


@router.get("/me", response_model=list[MyQueueEntry],
            summary="The caller's own place in today's and upcoming queues")
async def get_my_entries(viewer: Principal = Depends(current_principal), s: AsyncSession = Depends(get_session)):
    return await my_entries(s, viewer)


@router.post("/{queue_id}/call-next", response_model=CallNextResult,
             summary="Call the next waiting patient (queue's doctor or staff)")
async def post_call_next(queue_id: uuid.UUID, viewer: Principal = Depends(current_principal),
                         s: AsyncSession = Depends(get_session)):
    q = await get_queue_for_manager(s, queue_id, viewer)
    entry = await call_next(s, q)
    entry_id, key = entry.id, QueueKey.of(q)
    await s.commit()
    snap = await build_snapshot(s, key, viewer)
    await publish_snapshots([key])
    called = next(v for v in snap.current if v.entry_id == entry_id)
    return CallNextResult(called=called, queue=snap)


@router.patch("/{queue_id}/entries/{entry_id}", response_model=QueueSnapshot,
              summary="Change an entry's status (queue's doctor or staff)")
async def patch_entry(queue_id: uuid.UUID, entry_id: uuid.UUID, body: StatusUpdate,
                      viewer: Principal = Depends(current_principal), s: AsyncSession = Depends(get_session)):
    q = await get_queue_for_manager(s, queue_id, viewer)
    await change_status(s, q, entry_id, body.status)
    key = QueueKey.of(q)
    await s.commit()
    await publish_snapshots([key])
    return await build_snapshot(s, key, viewer)
