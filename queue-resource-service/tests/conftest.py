import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://queue:queue@localhost:5432/queue_test")
os.environ.update(DB_NULL_POOL="true", CONSUMER_ENABLED="false", AUTH_ALLOW_UNVERIFIED="true",
                  AUTH_JWKS_URL="", REDIS_URL="")

import jwt  # noqa: E402
import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DAY = "2026-11-10"


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    """Runs the real migrations up, and back down at the end (also tests the downgrade)."""
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest.fixture(autouse=True)
async def clean_tables():
    from app.db import engine

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE queue_entries, queues, appointment_versions, processed_events CASCADE"))
    yield


@pytest.fixture
async def client():
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


def token(user_id: uuid.UUID, *roles: str) -> dict:
    t = jwt.encode({"sub": str(user_id), "realm_access": {"roles": list(roles)}}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {t}"}


def event(kind: str, appointment_id: uuid.UUID, version: int, *, event_id: uuid.UUID | None = None,
          **payload) -> tuple[bytes, str]:
    """Builds a message body + routing key like appointment-service would publish."""
    import json

    for k, v in list(payload.items()):
        if isinstance(v, uuid.UUID):
            payload[k] = str(v)
    camel = "Appointment" + "".join(p.capitalize() for p in kind.split("_"))
    body = {
        "event_id": str(event_id or uuid.uuid4()),
        "event_type": camel,
        "event_version": 1,
        "aggregate_id": str(appointment_id),
        "aggregate_version": version,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "correlation_id": str(uuid.uuid4()),
        "producer": "appointment-service",
        "payload": payload,
    }
    return json.dumps(body).encode(), f"appointment.{kind}"


def booked(appointment_id, version, patient_id, doctor_id, start, day=DAY, **extra):
    return event("booked", appointment_id, version, patient_id=patient_id, doctor_id=doctor_id,
                 appointment_date=day, start_time=start, **extra)
