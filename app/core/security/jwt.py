import jwt
import uuid
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.core.config import settings


logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Base JWT xatoligi"""
 
 
class TokenExpiredError(JWTError):
    """Token muddati o'tgan"""
 
 
class InvalidTokenError(JWTError):
    """Token noto'g'ri"""
 
 
class TokenRevokedError(JWTError):
    """Token bekor qilingan"""
 
 
@dataclass
class TokenPayload:
    iss: str
    sub: int
    type: str
    jti: str = field(default_factory=lambda: str(uuid.uuid4()))
    iat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exp: Optional[datetime] = None
    roles: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)
 
    def to_dict(self) -> dict:
        return {
            "iss": self.iss,
            "sub": self.sub,
            "typ": self.type.value,
            "jti": self.jti,
            "iat": self.iat.timestamp(),
            "exp": self.exp.timestamp() if self.exp else None,
            "rol": self.roles,
            **self.extra,
        }
  

class JWTManager: 
    def __init__(self, blacklist_store=None):
        self.algorithm = settings.JWT_ALGORITHM
        self.public_key = settings.JWT_PUBLIC_KEY_PATH,
        self.private_key = settings.JWT_PRIVATE_KEY_PATH
        self.access_token_ttl = settings.JWT_ACCESS_TTL_MINUTES
        self.refresh_token_ttl = settings.JWT_REFRESH_TTL_DAYS
        self.issuer = settings.JWT_ISSUER
        self.audience = settings.JWT_AUDIENCE
        self._now = datetime.now(timezone.utc)
        self._blacklist: set[str] = blacklist_store if blacklist_store is not None else set()
 
    def create_access_token(
        self,
        user_id: str,
        roles: list[str] = None,
        extra: dict = None,
    ) -> str:
        payload = TokenPayload(
            sub=user_id,
            typ="access",
            iat=self._now,
            exp=self._now + timedelta(minutes=self.access_token_ttl),
            rol=roles or [],
            extra=extra or {},
        )
        return self._encode(payload)
 
    def create_refresh_token(self, user_id: str) -> str:
        payload = TokenPayload(
            sub=user_id,
            typ="refresh",
            iat=self._now,
            exp=self._now + timedelta(days=self.refresh_token_ttl),
        )
        return self._encode(payload)
 
    def create_token_pair(
        self,
        user_id: str,
        roles: list[str] = None,
    ) -> dict[str, str]:
        return {
            "access_token": self.create_access_token(user_id, roles),
            "refresh_token": self.create_refresh_token(user_id),
            "type": "Bearer",
            "exp": self.access_token_ttl * 60,
        }
 
    def verify_access_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != "access":
            raise InvalidTokenError("This is not an access token")
        return payload
 
    def verify_refresh_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("This is not a refresh token")
        return payload
 
    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        payload = self.verify_refresh_token(refresh_token)
        user_id = payload["sub"]
        roles = payload.get("roles", [])
        
        new_access = self.create_access_token(user_id, roles)
        logger.info(f"The access token has been updated: user={user_id}")
        return {
            "access_token": new_access,
            "type": "Bearer",
            "exp": self.refresh_token_ttl * 60,
        }
 
    def revoke_token(self, token: str) -> None:
        try:
            payload = self._decode(token)
            jti = payload.get("jti")
            if jti:
                self._blacklist.add(jti)
                logger.info(f"The token has been revoked: jti={jti}")
        except JWTError:
            pass
 
    @property
    def public_key_pem(self) -> bytes:
        return self.public_key
 
    def _encode(self, payload: TokenPayload) -> str:
        data = payload.to_dict()
        data["iss"] = self.issuer
        data["aud"] = self.audience
        return jwt.encode(
            data,
            self.private_key,
            algorithm=self.algorithm,
        )
 
    def _decode(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=self.algorithm,
                issuer=self.issuer,
                audience=self.audience,
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}")
 
        jti = payload.get("jti")
        if jti and jti in self._blacklist:
            raise TokenRevokedError("The token has been revoked")
 
        return payload