import hmac
import logging
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError, 
    VerificationError, 
    InvalidHashError
)

from app.core.config import settings


class Argon2PasswordHasher: 
    def __init__(self):
        self._hasher = PasswordHasher(
            time_cost=settings.TIME_COST,
            memory_cost=settings.MEMORY_COST,
            parallelism=settings.PARALLELISM,
            hash_len=settings.HASH_LEN,
            salt_len=settings.SALT_LEN,
        )

    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def _apply_pepper(self, password: str) -> str:
        if not settings.PEPPER:
            return password

        return hmac.new(
            key=settings.PEPPER.encode(settings.ENCODING),
            msg=password.encode(settings.ENCODING),
            digestmod="sha256",
        ).hexdigest()
 
    ####################################################################################
    # --- Hash -------------------------------------------------------------------------
    ####################################################################################

    def hash(self, password: str) -> str:
        prepared = self._apply_pepper(password)
        return self._hasher.hash(prepared)

    ####################################################################################
    # --- Verify -----------------------------------------------------------------------    
    ####################################################################################

    def verify(self, stored_hash: str, password: str) -> tuple[bool, str | None]:

        prepared = self._apply_pepper(password)

        try:
            is_valid = self._hasher.verify(stored_hash, prepared)
        except VerifyMismatchError:
            return False
        except (VerificationError, InvalidHashError) as e:
            logger.warning(f"Password hash is invalid or cannot be verified: {e}")

        if not is_valid:
            return False, None

        if self._hasher.check_needs_rehash(stored_hash):
            new_hash = self.hash(password)
            return True, new_hash

        return True, None    