"""Pushes queue snapshots to WebSocket clients (RealtimeBroadcaster in the class diagram).

With REDIS_URL set, updates go through Redis pub/sub so every service instance's clients
receive them, whichever instance processed the change. Without it, delivery is in-process."""
import asyncio
import contextlib
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

from app.config import settings

log = logging.getLogger(__name__)
CHANNEL = "clinilink.queue-updates"


class Broadcaster:
    def __init__(self, redis_url: str | None):
        self._redis_url = redis_url
        self._redis = None
        self._listener: asyncio.Task | None = None
        self._subscribers: dict[str, set[WebSocket]] = defaultdict(set)

    async def start(self) -> None:
        if self._redis_url:
            import redis.asyncio as redis

            self._redis = redis.from_url(self._redis_url)
            self._listener = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._listener:
            self._listener.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener
        if self._redis:
            await self._redis.aclose()

    async def status(self) -> str:
        if not self._redis:
            return "LOCAL"
        try:
            await self._redis.ping()
            return "UP"
        except Exception:
            return "DOWN"

    def subscribe(self, key: str, ws: WebSocket) -> None:
        self._subscribers[key].add(ws)

    def unsubscribe(self, key: str, ws: WebSocket) -> None:
        self._subscribers[key].discard(ws)
        if not self._subscribers[key]:
            del self._subscribers[key]

    async def publish(self, key: str, snapshot: dict) -> None:
        if self._redis:
            try:
                await self._redis.publish(CHANNEL, json.dumps({"key": key, "snapshot": snapshot}))
                return
            except Exception:
                log.warning("Redis publish failed, delivering to local clients only", exc_info=True)
        await self._deliver(key, snapshot)

    async def _deliver(self, key: str, snapshot: dict) -> None:
        for ws in list(self._subscribers.get(key, ())):
            try:
                await ws.send_json(snapshot)
            except Exception:
                self.unsubscribe(key, ws)

    async def _listen(self) -> None:
        while True:
            try:
                async with self._redis.pubsub() as pubsub:
                    await pubsub.subscribe(CHANNEL)
                    log.info("Subscribed to Redis channel %s", CHANNEL)
                    async for msg in pubsub.listen():
                        if msg["type"] == "message":
                            data = json.loads(msg["data"])
                            await self._deliver(data["key"], data["snapshot"])
            except asyncio.CancelledError:
                raise
            except Exception:
                log.warning("Redis listener failed, retrying in 2s", exc_info=True)
                await asyncio.sleep(2)


broadcaster = Broadcaster(settings.redis_url)


async def publish_snapshots(keys) -> None:
    """Sends the public snapshot of each changed queue. Never raises: a failed push must not
    undo a committed change, clients get the latest state on their next update or reconnect."""
    from app.db import SessionLocal
    from app.service import build_snapshot

    try:
        async with SessionLocal() as s:
            for key in keys:
                snap = await build_snapshot(s, key)
                await broadcaster.publish(key.channel, snap.model_dump(mode="json"))
    except Exception:
        log.exception("Could not push queue updates")
