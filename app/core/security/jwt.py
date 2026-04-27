import jwt
import uuid
import logging
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exception import InvalidIssuerError, InvalidTokenError, TokenExpiredError, TokenRevokedError
from app.modules.auth.repository import JWTTokenRepository


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
 
    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def create_access_token(self, user_id: int, roles: str or list[str]) -> str:
        
        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),
            "iat": self._now,
            "exp": self._now + timedelta(minutes=self.access_token_ttl),
            "rol": roles or []}

        return self._encode(payload)
 
    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

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
 
    ####################################################################################
    # --- Verify Access Token ----------------------------------------------------------    
    ####################################################################################

    async def verify_access_token(self, token: str) -> dict:
        payload = await self._decode(token)
        if (
            not payload.get("rol") or
            not self._is_access_token(payload)
        ):
            raise InvalidTokenError("This is not a access token")
            
        return payload
 
    ####################################################################################
    # --- Verify Refresh Token ---------------------------------------------------------    
    ####################################################################################

    async def verify_refresh_token(self, token: str) -> dict:
        payload = await self._decode(token)
        if (
            payload.get("rol") or
            not self._is_refresh_token(payload)
        ):
            raise InvalidTokenError()

        return payload

    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def create_token_pair(self, user_id: str, roles: list = None) -> dict:
        return {
            "access_token": self.create_access_token(user_id, roles),
            "refresh_token": self.create_refresh_token(user_id),
            "type": "Bearer",
            "exp": self.access_token_ttl * 60}
 
    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    async def refresh_access_token(self, refresh_token: str, roles: str or []) -> dict:
        payload = await self.verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        exp = payload.get('exp')
        
        new_access = self.create_access_token(user_id, roles)
        self.create_refresh_token(user_id=user_id, exp=exp)
        logger.info(f"The access token has been updated: user={user_id}")
        return {
            "access_token": new_access,
            "type": "Bearer",
            "exp": self._now + timedelta(minutes=self.access_token_ttl)}
 
    ####################################################################################
    # --- Is Access Token --------------------------------------------------------------    
    ####################################################################################        
 
    def _is_access_token(self, payload: dict) -> bool:
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not exp or not iat:
            return False

        lifetime = exp - iat

        return abs(lifetime - self.access_token_ttl * 60) < 5

    ####################################################################################
    # --- Is Refresh Token -------------------------------------------------------------    
    ####################################################################################

    def _is_refresh_token(self, payload: dict) -> bool:
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not exp or not iat:
            return False

        lifetime = exp - iat

        return abs(lifetime - self.refresh_token_ttl * 24 * 60 * 60) < 5  

    ####################################################################################
    # --- Encode JWT -------------------------------------------------------------------    
    #################################################################################### 

    def _encode(self, payload: dict) -> str:

        return jwt.encode(
            payload,
            self.read_file(self.private_key),
            algorithm=self.algorithm)
 
    ####################################################################################
    # --- Decode JWT -------------------------------------------------------------------    
    ####################################################################################

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
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise InvalidTokenError()

        is_revoked = await self._blacklist.jti_exists(user_id=user_id, jti=jti)
        if is_revoked:
            raise TokenRevokedError()
        return payload


print(JWT().create_access_token(user_id=1, roles="user"))
print(f"\n########################################################\n")
print(JWT().create_refresh_token(user_id=1))