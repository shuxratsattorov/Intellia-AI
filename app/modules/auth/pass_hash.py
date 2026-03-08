import os
import hmac
from __future__ import annotations
from typing import Literal
from dataclasses import dataclass
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

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
    def from_profile(cls, profile: ArgonProfile = "balanced") -> "Argon2idConfig":
        presets: dict[str, Argon2idConfig] = {
            "interactive": cls(
                time_cost=3,
                memory_cost=32 * 1024,
                parallelism=1,
                hash_len=32,
                salt_len=16,
                encoding="utf-8",
            ),
            "balanced": cls(
                time_cost=3,
                memory_cost=64 * 1024,
                parallelism=1,
                hash_len=32,
                salt_len=16,
                encoding="utf-8",
            ),
            "high_memory": cls(
                time_cost=4,
                memory_cost=128 * 1024,
                parallelism=1,
                hash_len=32,
                salt_len=16,
                encoding="utf-8",
            ),
        }
        return presets[profile]    

    @classmethod
    def from_settings(cls, profile: ArgonProfile = "balanced") -> "Argon2idConfig":
        base = cls.from_profile(profile)

        cfg = cls(
            time_cost=int(getattr(settings, "TIME_COST", base.time_cost)),
            memory_cost=int(getattr(settings, "MEMORY_COST", base.memory_cost)),
            parallelism=int(getattr(settings, "PARALLELISM", base.parallelism)),
            hash_len=int(getattr(settings, "HASH_LEN", base.hash_len)),
            salt_len=int(getattr(settings, "SALT_LEN", base.salt_len)),
            encoding=str(getattr(settings, "ENCODING", base.encoding)),
        )
        cfg.validate()
        return cfg


class PasswordHash:
    def __init__(self, config: Argon2idConfig, pepper: str | None = None) -> None:
        self.config = config
        self.pepper = pepper or settings.PASS_PEPPER
        self._hasher = self.config.to_password_hasher()

    def _apply_pepper(self, password: str) -> str:
        if not self.pepper:
            return password

        return hmac.new(
            key=self.pepper.encode(self.config.encoding),
            msg=password.encode(self.config.encoding),
            digestmod="sha256",
        ).hexdigest()

    def hash_password(self, password: str) -> str:
        prepared = self._apply_pepper(password)
        return self._hasher.hash(prepared)

    def verify_password(self, password_hash: str, password: str) -> bool:
        prepared = self._apply_pepper(password)

        try:
            return self._hasher.verify(password_hash, prepared)

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