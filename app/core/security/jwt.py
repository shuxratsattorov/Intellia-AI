import jwt
import uuid
import logging
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.modules.auth.repository import JWTTokenRepository
from app.core.error.exception import InvalidKeyError, TokenInvalidError
from app.core.error.exception import (
    TokenExpiredError, 
    TokenInvalidError,
    TokenRevokedError,
    InvalidIssuerError,
    InvalidSignatureError,
    ImmatureSignatureError
)


logger = logging.getLogger(__name__)

   
class JWT: 
    def __init__(self, blacklist_store=None):
        self.algorithm = settings.JWT_ALGORITHM
        self.public_key = settings.JWT_PUBLIC_KEY_PATH
        self.private_key = settings.JWT_PRIVATE_KEY_PATH
        self.access_token_ttl = settings.JWT_ACCESS_TTL_MINUTES
        self.refresh_token_ttl = settings.JWT_REFRESH_TTL_DAYS
        self.issuer = settings.JWT_ISSUER
        self._now = datetime.now(timezone.utc)
        self._blacklist = JWTTokenRepository()

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r") as f:
            return f.read()  

    # ---------------- Create Access Token ----------------    

    def create_access_token(self, user_id: int, roles: str or list[str]) -> str:
        
        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),
            "iat": self._now,
            "exp": self._now + timedelta(minutes=self.access_token_ttl),
            "rol": roles or []}

        return self._encode(payload)
 
    # ---------------- Create Refresh Token ----------------    

    def create_refresh_token(self, user_id: int, exp: int = None) -> str:
        expire_time = exp if exp is not None else self._now + timedelta(
            days=self.refresh_token_ttl)


        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),
            "iat": self._now,
            "exp": expire_time}

        return self._encode(payload)
 
    # ---------------- Verify Access Token ----------------    

    async def verify_access_token(self, token: str) -> dict:
        payload = await self._decode(token)
        if (
            not payload.get("rol") or
            not self._is_access_token(payload)
        ):
            raise TokenInvalidError
            
        return payload
 
    # ---------------- Verify Refresh Token ----------------    

    async def verify_refresh_token(self, token: str) -> dict:
        payload = await self._decode(token)
        if (
            payload.get("rol") or
            not self._is_refresh_token(payload)
        ):
            raise TokenInvalidError

        return payload

    # ---------------- Create Token Pair ----------------    

    def create_token_pair(self, user_id: str, roles: list = None) -> dict:
        return {
            "access_token": self.create_access_token(user_id, roles),
            "refresh_token": self.create_refresh_token(user_id),
            "type": "Bearer",
            "exp": self.access_token_ttl * 60}
 
     # ---------------- Is Access Token ----------------            
 
    def _is_access_token(self, payload: dict) -> bool:
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not exp or not iat:
            return False

        lifetime = exp - iat

        return abs(lifetime - self.access_token_ttl * 60) < 5

    # ---------------- Is Refresh Token ----------------    

    def _is_refresh_token(self, payload: dict) -> bool:
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not exp or not iat:
            return False

        lifetime = exp - iat

        return abs(lifetime - self.refresh_token_ttl * 24 * 60 * 60) < 5  

    # ---------------- Encode JWT ----------------    

    def _encode(self, payload: dict) -> str:
        try:
            token = jwt.encode(
                payload,
                self.read_file(self.private_key),
                algorithm=self.algorithm
            )
        except jwt.InvalidKeyError:
            raise InvalidKeyError()   

        return token     

     # ---------------- Decode JWT ----------------

    async def _decode(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.read_file(self.public_key),
                algorithms=self.algorithm,
                issuer=self.issuer
            )   
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()

        except jwt.InvalidIssuerError:
            raise InvalidIssuerError()

        except jwt.ImmatureSignatureError:
            raise ImmatureSignatureError() 

        except jwt.InvalidSignatureError:
            raise InvalidSignatureError()

        except jwt.DecodeError:
            raise TokenInvalidError()       

        except jwt.InvalidKeyError:
            raise InvalidKeyError()

        except jwt.InvalidTokenError:
            raise TokenInvalidError()

        # business logic
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not isinstance(user_id, str) or not user_id.isdigit():
            raise TokenInvalidError

        if not isinstance(jti, str) or not jti.strip():
            raise TokenInvalidError

        is_revoked = await self._blacklist.jti_exists(
            user_id=user_id, token=token, jti=jti
        )
        if is_revoked:
            raise TokenRevokedError()
        return payload