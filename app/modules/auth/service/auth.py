from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.error.exception import DefaultRoleNotConfigured, UserAlreadyExists, UserNotFoundError
from app.core.security.jwt import JWT
from app.modules.auth.repository.rbac import RoleRepository, UserRoleRepository
from app.modules.users.models import User
from app.modules.auth.repository.auth import (
    JWTTokenRepository, UserRepository, UserCredentialsRepository)
from app.core.security.password import Argon2PasswordHasher 
from app.infrastructure.cache.cache import RedisCache   



class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self._jwt = JWT()
        self._redis_cache = RedisCache()
        self._password_hash = Argon2PasswordHasher()
        self._user_repo = UserRepository(session)
        self._role_repo = RoleRepository(session)
        self._jwt_repo = JWTTokenRepository(session)
        self._user_role_repo = UserRoleRepository(session)
        self._credentials_repo = UserCredentialsRepository(session)

    # --- Register Service -------------------------------------------------------------

    async def register(self, email: str) -> User:

        if await self._user_repo.exists_by_email(email=email, is_verified=True):
            raise UserAlreadyExists

        default_role = await self._role_repo.get_by_name(settings.DEFAULT_ROLE)
        if not default_role:
            raise DefaultRoleNotConfigured

        user = await self._user_repo.create_user(
            email=email, is_active=True, is_verified=False
        )
        await self._user_role_repo.assign_role(user_id=user.id, role_id=default_role.id)

        return user

    async def verify_otp(self, email: str, otp: str, flow: str = "register") -> str:
        user = await self._user_repo.get_user_by_email(email)

        if not user:
            raise UserNotFoundError()

        if user.is_verified == True:
            raise UserAlreadyVerified()    

        cached_otp = await self._redis_cache.get_otp(flow, user.id) 

        if not cached_otp:
            raise Exception("OTP expired")   

        if otp != cached_otp:
            attempts = await self._redis_cache.increment_attempts(flow, user.id)

            if attempts >= 5:
                await self._redis_cache.block_user(flow, user.id)
                raise Exception("Too many attempts, user blocked")

            raise Exception("Invalid OTP")

        is_verified = await self._user_repo.set_verified(email=email)

        await self._redis_cache.cleanup_after_login(flow, user.id)    

        return is_verified

    async def set_password(self, email: str, password: str) -> str:
        user = await self._user_repo.get_user_by_email(email)

        if not user:
            raise UserNotFoundError()

        if not user.is_verified:
            raise Exception("User is not verified")

        existing = await self._credentials_repo.get_by_user_id(user.id)

        if existing:
            raise Exception("Password already set")

        await self._credentials_repo.create_password_hash(
                user_id=user.id,
                password_hash=self._password_hash.hash(password),
        )    

        return "Password set successfully"

    # --- Logout Service ---------------------------------------------------------------

    async def logout(self, refresh_token: str) -> str:
        payload = await self._jwt.verify_refresh_token(token=refresh_token)

        user_id = payload.get("sub")
        jti = payload.get("jti")

        revoke = await self._jwt_repo.revoke_token(
            user_id=user_id, token=refresh_token, jti=jti)

        return revoke




    # async def login(
    #     self,
    #     email: str,
    #     password: str,
    #     *,
    #     ip: str = "",
    #     user_agent: str = "",
    # ) -> TokenPair:
    #     """Authenticate user and return tokens."""
    #     email = email.strip().lower()
    #     user = await self._user_repo.get_by_email(email)
    #     if not user:
    #         raise AuthenticationError()

    #     credentials = await self._credentials_repo.get_by_user_id(user.id)
    #     if not credentials:
    #         raise AuthenticationError()

    #     if not self._password_hash.verify_password(credentials.password_hash, password):
    #         raise AuthenticationError()

    #     if not user.is_active:
    #         raise AuthenticationError("Account is deactivated")

    #     roles = [r.name for r in user.roles] if user.roles else []
    #     access_token, access_exp, _ = jwt.create_access_token(
    #         user_id=user.id,
    #         roles=roles,
    #     )
    #     refresh_token, refresh_exp, jti = jwt.create_refresh_token(user_id=user.id)

    #     rt = RefreshToken(
    #         user_id=user.id,
    #         token_jti=jti,
    #         ip=ip,
    #         user_agent=user_agent,
    #         expires_at=refresh_exp,
    #     )
    #     self.session.add(rt)
    #     await self.session.commit()

    #     return TokenPair(
    #         access_token=access_token,
    #         refresh_token=refresh_token,
    #         access_expires_at=_format_expires(access_exp),
    #         refresh_expires_at=_format_expires(refresh_exp),
    #     )

    # async def refresh_tokens(self, refresh_token: str) -> TokenPair:
    #     """Issue new token pair from valid refresh token."""
    #     try:
    #         payload = jwt.decode_token(refresh_token)
    #     except Exception:
    #         raise TokenError("Invalid or expired refresh token")

    #     if payload.get("type") != "refresh":
    #         raise TokenError("Invalid token type")

    #     jti = payload.get("jti")
    #     user_id = payload.get("sub")
    #     if not jti or not user_id:
    #         raise TokenError("Invalid token payload")

    #     rt = await self._refresh_repo.get_valid_by_jti(jti)
    #     if not rt:
    #         raise TokenError("Refresh token has been revoked or expired")

    #     user = await self._user_repo.get_by_id(int(user_id))
    #     if not user or not user.is_active:
    #         raise TokenError("User not found or inactive")

    #     roles = [r.name for r in user.roles] if user.roles else []
    #     access_token, access_exp, _ = jwt.create_access_token(
    #         user_id=user.id,
    #         roles=roles,
    #     )
    #     new_refresh, refresh_exp, new_jti = jwt.create_refresh_token(user_id=user.id)

    #     rt.revoked_at = datetime.now(timezone.utc)
    #     self.session.add(rt)

    #     new_rt = RefreshToken(
    #         user_id=user.id,
    #         token_jti=new_jti,
    #         expires_at=refresh_exp,
    #     )
    #     self.session.add(new_rt)
    #     await self.session.commit()

    #     return TokenPair(
    #         access_token=access_token,
    #         refresh_token=new_refresh,
    #         access_expires_at=_format_expires(access_exp),
    #         refresh_expires_at=_format_expires(refresh_exp),
    #     )

    # async def forgot_password(self, email: str) -> None:
    #     """Create password reset token and send email (placeholder)."""
    #     email = email.strip().lower()
    #     user = await self._user_repo.get_by_email(email)
    #     if not user:
    #         return

    #     raw_token = secrets.token_urlsafe(32)
    #     token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    #     expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    #     reset_token = PasswordResetToken(
    #         user_id=user.id,
    #         token_hash=token_hash,
    #         expires_at=expires_at,
    #     )
    #     self.session.add(reset_token)
    #     await self.session.commit()

    #     # TODO: Send email with reset link containing raw_token
    #     # For now, in production you would integrate with email service

    # async def reset_password(self, token: str, new_password: str) -> None:
    #     """Reset password using valid reset token."""
    #     token_hash = hashlib.sha256(token.encode()).hexdigest()
    #     reset_token = await self._reset_repo.get_valid_by_token_hash(token_hash)
    #     if not reset_token:
    #         raise TokenError("Invalid or expired reset token")

    #     credentials = await self._credentials_repo.get_by_user_id(reset_token.user_id)
    #     if not credentials:
    #         raise TokenError("User credentials not found")

    #     credentials.password_hash = self._password_hash.hash_password(new_password)
    #     reset_token.used_at = datetime.now(timezone.utc)
    #     self.session.add(credentials)
    #     self.session.add(reset_token)
    #     await self.session.commit()


class JWTService():
    def __init__(self, session: AsyncSession) -> None:
        self._jwt = JWT()
        self._jwt_repo = JWTTokenRepository(session)
        self._user_repo = UserRepository(session)

    async def refresh_access_token(self, refresh_token: str) -> dict:
        payload = await self._jwt.verify_refresh_token(token=refresh_token)

        user_id = payload.get("sub")
        exp = payload.get('exp')
        jti = payload.get("jti")
        
        current_roles = await self._user_repo.get_current_roles_by_user_id(
            user_id=user_id
        )
        new_access = self._jwt.create_access_token(user_id, current_roles)
        self._jwt.create_refresh_token(user_id=user_id, exp=exp)
        await self._jwt_repo.revoke_token(user_id=user_id, token=refresh_token, jti=jti)

        return {
            "access_token": new_access,
            "type": "Bearer"
        }

    async def revoke_token(self, refresh_token: str) -> str:
        payload = await self._jwt._decode(refresh_token)

        user_id = payload.get("sub")
        jti = payload.get("jti")

        revoke = await self._jwt_repo.revoke_token(
            user_id=user_id, token=refresh_token, jti=jti)

        return revoke



# logger.info(f"The token has been revoked: jti={jti}")















# await self.session.commit()
#             await self.session.refresh(user)
#             await self.session.rollback()