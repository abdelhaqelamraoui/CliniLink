# syntax=docker/dockerfile:1
# CliniLink MS4 - Queue & Resource Management Service
#   docker build -t clinilink/queue-resource-service:1.0 .            -> runtime image
#   docker build --target test -t clinilink/queue-resource-service:test .  -> image with the test suite

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# ---- dependencies (cached until requirements.txt changes) ----
FROM base AS deps
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---- test image: app + dev dependencies + tests ----
FROM base AS test
COPY --from=deps /install /usr/local
COPY requirements.txt requirements-dev.txt pyproject.toml alembic.ini ./
RUN pip install -r requirements-dev.txt
COPY migrations ./migrations
COPY app ./app
COPY tests ./tests
CMD ["pytest", "-q"]

# ---- runtime image (default target) ----
FROM base AS runtime
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --no-create-home app
COPY --from=deps /install /usr/local
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2)" || exit 1
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
