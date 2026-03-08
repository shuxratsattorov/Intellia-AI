import os
from __future__ import annotations
from typing import Literal
from argon2 import PasswordHasher
from dataclasses import dataclass

from app.core.config import settings


ArgonProfile = Literal["interactive", "balanced", "high_memory"]


@dataclass(frozen=True, slots=True)
class Argon2idConfig:

    time_cost: int
    memory_cost: int
    parallelism: int
    hash_len: int
    salt_len: int
    encoding: str    

    def validate(self) -> None:
        if self.time_cost < 1:
            raise ValueError("time_cost must be >= 1")

        if self.memory_cost < 19 * 1024:
            raise ValueError("memory_cost is too low; minimum recommended is 19 MiB (19456 KiB)")

        if self.parallelism < 1:
            raise ValueError("parallelism must be >= 1")

        if self.hash_len < 16:
            raise ValueError("hash_len should be >= 16 bytes")

        if self.salt_len < 16:
            raise ValueError("salt_len should be >= 16 bytes")

        if not self.encoding:
            raise ValueError("encoding must not be empty")

    def to_password_hasher(self) -> PasswordHasher:
        self.validate()
        return PasswordHasher(
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=self.hash_len,
            salt_len=self.salt_len,
            encoding=self.encoding,
        )

    @classmethod
    def from_env(cls, profile: ArgonProfile = "balanced") -> "Argon2idConfig":

        cfg = cls(
            time_cost=int(settings.TIME_COST),
            memory_cost=int(settings.MEMORY_COST),
            parallelism=int(settings.PARALLELISM),
            hash_len=int(settings.HASH_LEN),
            salt_len=int(settings.SALT_LEN),
            encoding=(settings.ENCODING),
        )
        cfg.validate()
        return cfg


class PasswordService:
    def __init__(self, config: Argon2idConfig | None = None, pepper: str | None = None) -> None:
        self.config = config or Argon2idConfig()
        self.pepper = pepper or os.getenv("PASSWORD_PEPPER", "")

        self._hasher = PasswordHasher(
            time_cost=self.config.time_cost,
            memory_cost=self.config.memory_cost,
            parallelism=self.config.parallelism,
            hash_len=self.config.hash_len,
            salt_len=self.config.salt_len,
            encoding=self.config.encoding,
        )

    def _apply_pepper(self, password: str) -> str:
        if not self.pepper:
            return password
        return hmac.new(
            key=self.pepper.encode(self.config.encoding),
            msg=password.encode(self.config.encoding),
            digestmod="sha256",
        ).hexdigest()

    def hash_password(self, password: str) -> str:
        self._validate_password_input(password)
        prepared = self._apply_pepper(password)
        return self._hasher.hash(prepared)

    def verify_password(self, stored_hash: str, password: str) -> bool:
        self._validate_password_input(password)
        prepared = self._apply_pepper(password)

        try:
            return self._hasher.verify(stored_hash, prepared)
        except VerifyMismatchError:
            return False
        except (VerificationError, InvalidHashError) as exc:
            raise ValueError("Password hash is invalid or cannot be verified") from exc

    def verify_and_update(self, stored_hash: str, password: str) -> tuple[bool, str | None]:
        is_valid = self.verify_password(stored_hash, password)
        if not is_valid:
            return False, None

        if self._hasher.check_needs_rehash(stored_hash):
            new_hash = self.hash_password(password)
            return True, new_hash

        return True, None

    @staticmethod
    def _validate_password_input(password: str) -> None:
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        if password == "":
            raise ValueError("Password must not be empty")