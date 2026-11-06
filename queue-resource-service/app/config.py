from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration, read from environment variables (e.g. DATABASE_URL)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "queue-resource-service"
    log_level: str = "INFO"
    timezone: str = "Europe/Paris"  # used for "today" and estimated times

    database_url: str = "postgresql+asyncpg://queue:queue@localhost:5432/queue_db"
    db_null_pool: bool = False  # tests only

    rabbitmq_url: str = "amqp://clinilink:clinilink@localhost:5672/clinilink"
    rabbitmq_queue: str = "queue-resource-service.appointment-events"
    rabbitmq_prefetch: int = 10
    consumer_enabled: bool = True

    # Redis pub/sub fans queue updates out to every instance's WebSocket clients.
    # Empty = in-process only (fine for a single instance).
    redis_url: str | None = None

    # Keycloak token validation. Set AUTH_JWKS_URL in any real deployment.
    auth_jwks_url: str | None = None
    auth_issuer: str | None = None
    auth_audience: str | None = None
    # Dev only: accept tokens without checking the signature (until Keycloak is set up).
    auth_allow_unverified: bool = False

    @field_validator("redis_url", "auth_jwks_url", "auth_issuer", "auth_audience", mode="before")
    @classmethod
    def _empty_is_none(cls, v):
        return v or None


settings = Settings()
