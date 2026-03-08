import jwt
from __future__ import annotations
from uuid import uuid4
from pathlib import Path
from datetime import datetime, timedelta, timezone

from app.core.config import settings


PRIVATE_KEY = Path(settings.JWT_PRIVATE_KEY).read_text()
PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY).read_text()


def create_access_token(*, user_id: int, roles: list[str]) -> tuple[str, datetime, str]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)
    jti = str(uuid4())

    payload = {
        "sub": user_id,
        "roles": roles,
        "type": "access",
        "jti": jti,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, exp, jti


def create_refresh_token(*, user_id: int) -> tuple[str, datetime, str]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    jti = str(uuid4())

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, exp, jti


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )
