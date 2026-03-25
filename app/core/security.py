import jwt
import hmac
import uuid
import logging
from enum import Enum
from pathlib import Path
from typing import Optional
from argon2.exceptions import (
    VerifyMismatchError, 
    VerificationError, 
    InvalidHashError
)
from argon2 import PasswordHasher
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger(__name__)
  
class JWTError(Exception):
    """Base JWT xatoligi"""
 
 
class TokenExpiredError(JWTError):
    """Token muddati o'tgan"""
 
 
class InvalidTokenError(JWTError):
    """Token noto'g'ri"""
 
 
class TokenRevokedError(JWTError):
    """Token bekor qilingan"""


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class Argon2Config:
    time_cost: int
    memory_cost: int
    parallelism: int
    hash_len: int
    salt_len: int
    encoding: str
    pepper: str
 
    @classmethod
    def high_security(cls) -> "Argon2Config":
        return cls(
            time_cost=4,
            memory_cost=262144,
            parallelism=4,
        )
 
    @classmethod
    def fast(cls) -> "Argon2Config":
        return cls(
            time_cost=1, 
            memory_cost=8192, 
            parallelism=1
        )
 
  
class PasswordHasher: 
    def __init__(self, config: Argon2Config = None):
        cfg = config or Argon2Config()
        self._hasher = PasswordHasher(
            time_cost=cfg.time_cost,
            memory_cost=cfg.memory_cost,
            parallelism=cfg.parallelism,
            hash_len=cfg.hash_len,
            salt_len=cfg.salt_len,
            encoding=cfg.encoding,
            pepper=cfg.pepper
        )

    def _apply_pepper(self, password: str) -> str:
        if not self.pepper:
            return password

        return hmac.new(
            key=self.pepper.encode(self.config.encoding),
            msg=password.encode(self.config.encoding),
            digestmod="sha256",
        ).hexdigest()
 
    def hash(self, password: str) -> str:
        prepared = self._apply_pepper(password)
        return self._hasher.hash(prepared)
 
    def verify(self, hashed: str, plain: str) -> bool:
        prepared = self._apply_pepper(plain)
        try:
            return self._hasher.verify(hashed, prepared)
        except VerifyMismatchError:
            return False
        except (VerificationError, InvalidHashError) as e:
            logger.warning(f"Password hash is invalid or cannot be verified: {e}")
            return False
 
    def needs_rehash(self, hashed: str) -> bool:
 
        return self._hasher.check_needs_rehash(hashed)

    def verify_and_update(self, stored_hash: str, password: str) -> tuple[bool, str | None]:
        is_valid = self.verify_password(stored_hash, password)

        if not is_valid:
            return False, None

        if self._hasher.check_needs_rehash(stored_hash):
            new_hash = self.hash_password(password)
            return True, new_hash

        return True, None
 
 
@dataclass(frozen=True)
class RSAKeyPair:
    private_key: bytes
    public_key: bytes
 
    @classmethod
    def generate(cls, key_size: int = 2048) -> "RSAKeyPair":
        private = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend(),
        )
        private_pem = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return cls(private_key=private_pem, public_key=public_pem)
 
    @classmethod
    def load(cls, private_key_path: str, public_key_path: str) -> "RSAKeyPair":
        return cls(
            private_key=Path(private_key_path).read_bytes(),
            public_key=Path(public_key_path).read_bytes(),
        )
 
    def save(self, private_key_path: str, public_key_path: str) -> None:
        priv = Path(private_key_path)
        pub = Path(public_key_path)
        priv.write_bytes(self.private_key)
        priv.chmod(0o600)
        pub.write_bytes(self.public_key)
        logger.info(f"RSA keys saved: {private_key_path}, {public_key_path}")
 
    
@dataclass(frozen=True)
class TokenConfig:
    key_pair: RSAKeyPair
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    issuer: str = "myapp"
    audience: str = "myapp-users"
 
 
@dataclass
class TokenPayload:
    sub: int
    type: TokenType
    jti: str = field(default_factory=lambda: str(uuid.uuid4()))
    iat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exp: Optional[datetime] = None
    roles: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)
 
    def to_dict(self) -> dict:
        return {
            "sub": self.sub,
            "type": self.type.value,
            "jti": self.jti,
            "iat": self.iat.timestamp(),
            "exp": self.exp.timestamp() if self.exp else None,
            "roles": self.roles,
            **self.extra,
        }
  
 
class JWTManager: 
    def __init__(self, config: TokenConfig, blacklist_store=None):
        self._config = config
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
            type=TokenType.ACCESS,
            iat=self._now,
            exp=self._now + timedelta(minutes=self._config.access_token_expire_minutes),
            roles=roles or [],
            extra=extra or {},
        )
        return self._encode(payload)
 
    def create_refresh_token(self, user_id: str) -> str:
        payload = TokenPayload(
            sub=user_id,
            type=TokenType.REFRESH,
            iat=self._now,
            exp=self._now + timedelta(days=self._config.refresh_token_expire_days),
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
            "exp": self._config.access_token_expire_minutes * 60,
        }
 
    def verify_access_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != TokenType.ACCESS.value:
            raise InvalidTokenError("This is not an access token")
        return payload
 
    def verify_refresh_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != TokenType.REFRESH.value:
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
            "exp": self._config.access_token_expire_minutes * 60,
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
        return self._config.key_pair.public_key
 
    def _encode(self, payload: TokenPayload) -> str:
        data = payload.to_dict()
        data["iss"] = self._config.issuer
        data["aud"] = self._config.audience
        return jwt.encode(
            data,
            self._config.key_pair.private_key,
            algorithm=self._config.algorithm,
        )
 
    def _decode(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self._config.key_pair.public_key,
                algorithms=[self._config.algorithm],
                issuer=self._config.issuer,
                audience=self._config.audience,
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}")
 
        jti = payload.get("jti")
        if jti and jti in self._blacklist:
            raise TokenRevokedError("The token has been revoked")
 
        return payload
 