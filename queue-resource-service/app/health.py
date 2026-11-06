from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.consumer import consumer
from app.db import engine
from app.realtime import broadcaster

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Process is running")
async def live():
    return {"status": "UP"}


@router.get("/health/ready", summary="Ready to serve traffic")
async def ready():
    """Only the database is required. If RabbitMQ or Redis is down, the service still serves
    queues (possibly stale), so it reports DEGRADED instead of going out of rotation."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database = "UP"
    except Exception:
        database = "DOWN"
    checks = {
        "database": database,
        "broker": "DISABLED" if not settings.consumer_enabled else ("UP" if consumer.connected else "DOWN"),
        "realtime": await broadcaster.status(),
    }
    if database == "DOWN":
        status = "DOWN"
    elif "DOWN" in checks.values():
        status = "DEGRADED"
    else:
        status = "UP"
    return JSONResponse({"status": status, "checks": checks}, status_code=503 if status == "DOWN" else 200)
