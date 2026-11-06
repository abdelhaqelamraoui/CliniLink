"""Consumes appointment events from RabbitMQ (queue declared by infra/rabbitmq/definitions.json).

Delivery rules (report section 6.5):
- ack only after the database commit
- duplicates are detected by event_id, out-of-order events by aggregate_version
- invalid messages are rejected straight to the dead-letter queue
- transient failures are requeued; RabbitMQ dead-letters after 3 attempts (x-delivery-limit)"""
import asyncio
import enum
import logging

import aio_pika
from pydantic import ValidationError

from app.config import settings
from app.db import SessionLocal
from app.events import NEEDS_PAYLOAD, AppointmentPayload, EventEnvelope, event_action
from app.logging_setup import correlation_id_var
from app.realtime import publish_snapshots
from app.service import QueueKey, apply_event

log = logging.getLogger(__name__)


class Outcome(str, enum.Enum):
    ACK = "ack"
    DUPLICATE = "duplicate"
    REJECT = "reject"  # permanent: malformed message -> DLQ
    RETRY = "retry"  # transient: requeue


async def process_message(body: bytes, routing_key: str | None) -> tuple[Outcome, set[QueueKey]]:
    try:
        env = EventEnvelope.model_validate_json(body)
        action = event_action(routing_key, env.event_type)
        payload = AppointmentPayload.model_validate(env.payload) if action in NEEDS_PAYLOAD else None
    except ValidationError as exc:
        log.error("Rejecting invalid message (routing key %s): %s", routing_key, exc)
        return Outcome.REJECT, set()

    token = correlation_id_var.set(env.correlation_id or str(env.event_id))
    try:
        async with SessionLocal() as s, s.begin():
            keys = await apply_event(s, env, action, payload)
        if keys is None:
            return Outcome.DUPLICATE, set()
        log.info("Processed %s (%s) for appointment %s", env.event_type, env.event_id, env.aggregate_id)
        return Outcome.ACK, keys
    except Exception:
        log.exception("Failed to process event %s, will retry", env.event_id)
        return Outcome.RETRY, set()
    finally:
        correlation_id_var.reset(token)


class AppointmentEventConsumer:
    def __init__(self) -> None:
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    @property
    def connected(self) -> bool:
        # is_closed stays False while a robust connection is reconnecting; the event is cleared then.
        return self._connection is not None and self._connection.connected.is_set()

    async def _handle(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        outcome, keys = await process_message(message.body, message.routing_key)
        if outcome == Outcome.REJECT:
            await message.reject(requeue=False)
        elif outcome == Outcome.RETRY:
            attempt = int((message.headers or {}).get("x-delivery-count", 0) or 0)
            await asyncio.sleep(min(2 ** attempt, 10))  # back off before the next attempt
            await message.nack(requeue=True)
        else:
            await message.ack()
            if keys:
                await publish_snapshots(keys)

    async def run(self) -> None:
        """Keeps consuming; reconnects if the broker is down or restarts.
        While the broker is unavailable the HTTP API still serves (possibly stale) queues."""
        while True:
            try:
                self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
                async with self._connection:
                    channel = await self._connection.channel()
                    await channel.set_qos(prefetch_count=settings.rabbitmq_prefetch)
                    queue = await channel.declare_queue(settings.rabbitmq_queue, passive=True)
                    log.info("Consuming from %s", settings.rabbitmq_queue)
                    async with queue.iterator() as messages:
                        async for message in messages:
                            await self._handle(message)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("RabbitMQ consumer stopped (%s), reconnecting in 5s", exc)
                await asyncio.sleep(5)


consumer = AppointmentEventConsumer()
