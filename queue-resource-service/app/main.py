import asyncio
import contextlib
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app import api, health, ws
from app.config import settings
from app.consumer import consumer
from app.db import engine
from app.errors import install_error_handlers
from app.logging_setup import correlation_id_var, setup_logging
from app.realtime import broadcaster

setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await broadcaster.start()
    consumer_task = asyncio.create_task(consumer.run()) if settings.consumer_enabled else None
    yield
    if consumer_task:
        consumer_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await consumer_task
    await broadcaster.stop()
    await engine.dispose()


app = FastAPI(
    title="CliniLink Queue & Resource Management Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/queues/docs",
    openapi_url="/api/v1/queues/openapi.json",
)


@app.middleware("http")
async def correlation_id(request: Request, call_next):
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = cid
    token = correlation_id_var.set(cid)
    try:
        response = await call_next(request)
    finally:
        correlation_id_var.reset(token)
    response.headers["X-Correlation-ID"] = cid
    return response


install_error_handlers(app)
app.include_router(health.router)
app.include_router(api.router)
app.include_router(ws.router)
