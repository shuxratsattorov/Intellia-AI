import jwt
import uuid
import logging
from datetime import datetime, timedelta, timezone

from app.modules.auth.repository import RefreshTokenRepository

from app.core.config import settings


logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Base JWT xatoligi"""
 
 
class TokenExpiredError(JWTError):
    """Token muddati o'tgan"""


class InvalidIssuerError(JWTError):
    "Invalid issuer"

 
class InvalidTokenError(JWTError):
    """Token noto'g'ri"""
 
 
class TokenRevokedError(JWTError):
    """Token bekor qilingan"""
   

class JWT: 
    def __init__(self, blacklist_store=None):
        self.algorithm = settings.JWT_ALGORITHM
        self.public_key = settings.JWT_PUBLIC_KEY_PATH
        self.private_key = settings.JWT_PRIVATE_KEY_PATH
        self.access_token_ttl = settings.JWT_ACCESS_TTL_MINUTES
        self.refresh_token_ttl = settings.JWT_REFRESH_TTL_DAYS
        self.issuer = settings.JWT_ISSUER
        self._now = datetime.now(timezone.utc)
        self._blacklist = RefreshTokenRepository()

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
            "rol": roles or []
            }
        return self._encode(payload)
 
    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def create_refresh_token(self, user_id: int) -> str:

        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "jti": str(uuid.uuid4()),
            "iat": self._now,
            "exp": self._now + timedelta(days=self.refresh_token_ttl)
            }
        return self._encode(payload)
 
    ####################################################################################
    # --- Verify Access Token ----------------------------------------------------------    
    ####################################################################################

    def verify_access_token(self, token: str) -> dict:
        payload = self._decode(token)
        if (
            not payload.get("rol") or
            not self._is_access_token(payload)
        ):
            raise InvalidTokenError("This is not a access token")
            
        return payload
 
    ####################################################################################
    # --- Verify Refresh Token ---------------------------------------------------------    
    ####################################################################################

    def verify_refresh_token(self, token: str) -> dict:
        payload = self._decode(token)
        if (
            payload.get("rol") or
            not self._is_refresh_token(payload)
        ):
            raise InvalidTokenError("This is not a refresh token")

        return payload

    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def create_token_pair(self, user_id: str, roles: list = None) -> dict:
        return {
            "access_token": self.create_access_token(user_id, roles),
            "refresh_token": self.create_refresh_token(user_id),
            "type": "Bearer",
            "exp": self.access_token_ttl * 60,
        }
 
    ####################################################################################
    # --- Apply Pepper Hmac ------------------------------------------------------------    
    ####################################################################################

    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        payload = self.verify_refresh_token(refresh_token)
        user_id = payload["sub"]

        roles = ""
        
        new_access = self.create_access_token(user_id, roles)
        logger.info(f"The access token has been updated: user={user_id}")
        return {
            "access_token": new_access,
            "type": "Bearer",
            "exp": self._now + timedelta(minutes=self.access_token_ttl),
        }
 
    ####################################################################################
    # --- Revoke Token -----------------------------------------------------------------   
    ####################################################################################

    def revoke_token(self, token: str) -> None:
        try:
            payload = self._decode(token)
            jti = payload.get("jti")
            if jti:
                self._blacklist.add(jti)
                logger.info(f"The token has been revoked: jti={jti}")
        except JWTError:
            pass
 
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
            algorithm=self.algorithm
        )
 
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
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidIssuerError:
            raise InvalidIssuerError("Invalid issuer")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}")
 
        jti = payload.get("jti")
        if jti:
            is_revoked = await self._blacklist.get_revoke_jti(jti=jti)
            if is_revoked:
                raise TokenRevokedError("The token has been revoked")
 
        return payload


access_token = JWT().create_access_token(user_id=1, roles="admin")
refresh_token = JWT().create_refresh_token(user_id=1)

print(access_token)
print("\n#############################################################################\n")
print(refresh_token)


print(JWT().verify_access_token(access_token))
print(JWT().verify_refresh_token(refresh_token))