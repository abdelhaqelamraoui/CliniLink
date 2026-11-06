"""Live queue updates (FR21). Public, anonymized snapshots, so waiting-room screens can connect
without a login. On connect the client gets the current snapshot, then one message per change."""
import logging
import uuid
from datetime import date

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.db import SessionLocal
from app.models import QueueType
from app.realtime import broadcaster
from app.service import QueueKey, build_snapshot, today

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ws/queues")


async def _serve(ws: WebSocket, key: QueueKey) -> None:
    await ws.accept()
    broadcaster.subscribe(key.channel, ws)
    try:
        async with SessionLocal() as s:
            snap = await build_snapshot(s, key)
        await ws.send_json(snap.model_dump(mode="json"))
        while True:
            await ws.receive_text()  # clients don't need to send anything; this detects disconnects
    except WebSocketDisconnect:
        pass
    finally:
        broadcaster.unsubscribe(key.channel, ws)


@router.websocket("/doctors/{doctor_id}")
async def ws_doctor_queue(ws: WebSocket, doctor_id: uuid.UUID, day: date | None = Query(default=None, alias="date")):
    await _serve(ws, QueueKey(QueueType.DOCTOR, doctor_id, day or today()))


@router.websocket("/resources/{resource_id}")
async def ws_resource_queue(ws: WebSocket, resource_id: uuid.UUID, day: date | None = Query(default=None, alias="date")):
    await _serve(ws, QueueKey(QueueType.RESOURCE, resource_id, day or today()))
