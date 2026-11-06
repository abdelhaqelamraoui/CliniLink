"""Token handling. Keycloak authenticates, the gateway validates; this service still checks
the token itself and enforces ownership (report section 6.2: "services enforce authorization")."""
import asyncio
import logging
import uuid
from dataclasses import dataclass

import jwt
from fastapi import Header

from app.config import settings
from app.errors import ProblemError
from app.models import QueueType

log = logging.getLogger(__name__)

STAFF_ROLES = frozenset({"STAFF", "ADMIN", "SUPER_ADMIN"})
_jwks_client = jwt.PyJWKClient(settings.auth_jwks_url, cache_keys=True) if settings.auth_jwks_url else None

if not _jwks_client and settings.auth_allow_unverified:
    log.warning("AUTH_ALLOW_UNVERIFIED is on: token signatures are NOT checked. Dev only.")


@dataclass(frozen=True)
class Principal:
    user_id: uuid.UUID
    roles: frozenset[str]

    @property
    def is_staff(self) -> bool:
        return bool(self.roles & STAFF_ROLES)

    def can_manage(self, queue_type: QueueType, owner_id: uuid.UUID) -> bool:
        """Staff and admins manage every queue; a doctor manages only their own queue."""
        if self.is_staff:
            return True
        return queue_type == QueueType.DOCTOR and "DOCTOR" in self.roles and self.user_id == owner_id


def _unauthorized(detail: str) -> ProblemError:
    return ProblemError(401, "UNAUTHORIZED", "Unauthorized", detail)


async def _decode(token: str) -> dict:
    if _jwks_client:
        key = (await asyncio.to_thread(_jwks_client.get_signing_key_from_jwt, token)).key
        return jwt.decode(
            token, key, algorithms=["RS256"],
            audience=settings.auth_audience, issuer=settings.auth_issuer,
            options={"verify_aud": settings.auth_audience is not None, "verify_iss": settings.auth_issuer is not None},
        )
    if settings.auth_allow_unverified:
        return jwt.decode(token, options={"verify_signature": False})
    raise ProblemError(503, "AUTH_NOT_CONFIGURED", "Authentication Not Configured",
                       "Set AUTH_JWKS_URL (or AUTH_ALLOW_UNVERIFIED=true for local development).")


def principal_from_claims(claims: dict) -> Principal:
    try:
        user_id = uuid.UUID(str(claims["sub"]))
    except (KeyError, ValueError):
        raise _unauthorized("Token subject is missing or is not a UUID.")
    roles = list(claims.get("realm_access", {}).get("roles", [])) + list(claims.get("roles", []))
    return Principal(user_id=user_id, roles=frozenset(r.upper() for r in roles))


async def current_principal(authorization: str | None = Header(default=None)) -> Principal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing bearer token.")
    try:
        claims = await _decode(authorization[7:].strip())
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc}")
    return principal_from_claims(claims)
