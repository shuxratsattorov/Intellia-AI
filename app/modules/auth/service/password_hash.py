import hmac
import logging
from dataclasses import dataclass
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError, 
    VerificationError, 
    InvalidHashError
)

from app.core.config import settings

 
logger = logging.getLogger(__name__)
 

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
