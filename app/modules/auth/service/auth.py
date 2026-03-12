from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.users.models import User
from app.modules.auth.models.auth import UserCredentials, RefreshToken, PasswordResetToken
from app.modules.auth.models.role_permission import Role
from app.modules.auth.repository.auth import (
    UserRepository,
    UserCredentialsRepository,
    RefreshTokenRepository,
    PasswordResetTokenRepository,
)
from app.modules.auth.repository.role_permission import RoleRepository, UserRoleRepository
from app.modules.auth.service.password_hash import PasswordHash, Argon2idConfig
from app.modules.auth.service import jwt
from app.modules.auth.schemas.schemas import TokenPair
from app.core.errors import (
    RegistrationError,
    AuthenticationError,
    TokenError,
)


def _format_expires(exp: datetime) -> str:
    """Format expiry datetime for API response."""
    return exp.isoformat()


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        password_hash: PasswordHash | None = None,
    ) -> None:
        self.session = session
        self._user_repo = UserRepository(session)
        self._credentials_repo = UserCredentialsRepository(session)
        self._refresh_repo = RefreshTokenRepository(session)
        self._reset_repo = PasswordResetTokenRepository(session)
        self._role_repo = RoleRepository(session)
        self._user_role_repo = UserRoleRepository(session)
        self._password_hash = password_hash or PasswordHash(Argon2idConfig.from_settings())

    async def register(self, email: str, password: str) -> tuple[User, TokenPair]:
        if await self._user_repo.exists_by_email(email):
            raise RegistrationError("A user with this email already exists")

        default_role = await self._role_repo.get_by_name(settings.DEFAULT_ROLE_NAME)
        if not default_role:
            raise RegistrationError("Default role 'user' is not configured")

        user = await self._user_repo.create_user(email=email, is_active=True)
        await self._credentials_repo.create_password_hash(
            user_id=user.id,
            password_hash=self._password_hash.hash_password(password),
        )
        await self._user_role_repo.assign_role(user_id=user.id, role_id=default_role.id)

        access_token, access_exp, _ = jwt.create_access_token(
            user_id=user.id,
            roles=[default_role.name],
        )
        refresh_token, refresh_exp, jti = jwt.create_refresh_token(user_id=user.id)

        await self._refresh_repo.create_refresh_token(
            user_id=user.id, 
            token_jti=jti, 
            expires_at=refresh_exp
        )

        await self.session.commit()
        await self.session.refresh(user)

        tokens = TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=_format_expires(access_exp),
            refresh_expires_at=_format_expires(refresh_exp),
        )
        return user, tokens

    async def login(
        self,
        email: str,
        password: str,
        *,
        ip: str = "",
        user_agent: str = "",
    ) -> TokenPair:
        """Authenticate user and return tokens."""
        email = email.strip().lower()
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError()

        credentials = await self._credentials_repo.get_by_user_id(user.id)
        if not credentials:
            raise AuthenticationError()

        if not self._password_hash.verify_password(credentials.password_hash, password):
            raise AuthenticationError()

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        roles = [r.name for r in user.roles] if user.roles else []
        access_token, access_exp, _ = jwt.create_access_token(
            user_id=user.id,
            roles=roles,
        )
        refresh_token, refresh_exp, jti = jwt.create_refresh_token(user_id=user.id)

        rt = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            ip=ip,
            user_agent=user_agent,
            expires_at=refresh_exp,
        )
        self.session.add(rt)
        await self.session.commit()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=_format_expires(access_exp),
            refresh_expires_at=_format_expires(refresh_exp),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Issue new token pair from valid refresh token."""
        try:
            payload = jwt.decode_token(refresh_token)
        except Exception:
            raise TokenError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise TokenError("Invalid token type")

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise TokenError("Invalid token payload")

        rt = await self._refresh_repo.get_valid_by_jti(jti)
        if not rt:
            raise TokenError("Refresh token has been revoked or expired")

        user = await self._user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise TokenError("User not found or inactive")

        roles = [r.name for r in user.roles] if user.roles else []
        access_token, access_exp, _ = jwt.create_access_token(
            user_id=user.id,
            roles=roles,
        )
        new_refresh, refresh_exp, new_jti = jwt.create_refresh_token(user_id=user.id)

        rt.revoked_at = datetime.now(timezone.utc)
        self.session.add(rt)

        new_rt = RefreshToken(
            user_id=user.id,
            token_jti=new_jti,
            expires_at=refresh_exp,
        )
        self.session.add(new_rt)
        await self.session.commit()

        return TokenPair(
            access_token=access_token,
            refresh_token=new_refresh,
            access_expires_at=_format_expires(access_exp),
            refresh_expires_at=_format_expires(refresh_exp),
        )

    async def logout(self, refresh_token: str) -> bool:
        """Revoke refresh token. Returns True if token was found and revoked."""
        try:
            payload = jwt.decode_token(refresh_token)
        except Exception:
            return False

        jti = payload.get("jti")
        if not jti:
            return False

        revoked = await self._refresh_repo.revoke_by_jti(jti)
        if revoked:
            await self.session.commit()
        return revoked

    async def forgot_password(self, email: str) -> None:
        """Create password reset token and send email (placeholder)."""
        email = email.strip().lower()
        user = await self._user_repo.get_by_email(email)
        if not user:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(reset_token)
        await self.session.commit()

        # TODO: Send email with reset link containing raw_token
        # For now, in production you would integrate with email service

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password using valid reset token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        reset_token = await self._reset_repo.get_valid_by_token_hash(token_hash)
        if not reset_token:
            raise TokenError("Invalid or expired reset token")

        credentials = await self._credentials_repo.get_by_user_id(reset_token.user_id)
        if not credentials:
            raise TokenError("User credentials not found")

        credentials.password_hash = self._password_hash.hash_password(new_password)
        reset_token.used_at = datetime.now(timezone.utc)
        self.session.add(credentials)
        self.session.add(reset_token)
        await self.session.commit()
