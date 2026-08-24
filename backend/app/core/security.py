"""JWT, хеширование паролей и работа с токенами."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    jti = str(uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def create_access_token(subject: str, *, extra_claims: dict[str, Any] | None = None) -> str:
    token, _, _ = _create_token(
        subject=subject,
        token_type=TOKEN_TYPE_ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims=extra_claims,
    )
    return token


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    return _create_token(
        subject=subject,
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
