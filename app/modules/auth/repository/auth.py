from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from datetime import datetime, timezone

from app.main import datatime
from app.modules.users.models import User
from app.db.base_repo import AsyncRepository
from app.modules.auth.models.auth import (
    RefreshToken,
    UserCredentials
)


class UserRepository(AsyncRepository[User]):
    model = User

    async def exists_by_email(self, email: str, is_verified: bool) -> bool:
        stmt = select(User.id).where(User.email == email, is_verified=is_verified).limit(1)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def get_id_by_email(self, email: str) -> int | None:
        stmt = select(User.id).where(User.email == email)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_user(self, email: str, is_active: bool, is_verified: bool) -> User:
        user = User(
        email=email,
        is_active=is_active,
        is_verified=is_verified
        )
        self.session.add(user)
        await self.session.flush()
        
        return user

        
class UserCredentialsRepository(AsyncRepository[UserCredentials]):
    model = UserCredentials

    async def get_by_user_id(self, user_id: int) -> UserCredentials | None:
        stmt = select(UserCredentials).where(UserCredentials.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_password_hash(self, user_id: int, password_hash: str):
        credentials = UserCredentials(
            user_id=user_id,
            password_hash=password_hash,
        )
        self.session.add(credentials)
        await self.session.flush()    


class RefreshTokenRepository(AsyncRepository[RefreshToken]):
    """Repository for RefreshToken entity."""

    model = RefreshToken

    async def get_valid_by_jti(self, jti: str) -> RefreshToken | None:
        """Fetch non-revoked refresh token by JTI."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_jti == jti,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        """Fetch refresh token by JTI (any status)."""
        stmt = select(RefreshToken).where(RefreshToken.token_jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_by_jti(self, jti: str) -> bool:
        """Revoke refresh token by JTI. Returns True if token was found and revoked."""
        token = await self.get_by_jti(jti)
        if token is None:
            return False
        token.revoked_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
        return True

    async def create_refresh_token(self, user_id: int, token_jti: str, expires_at: datatime) -> RefreshToken:  
        rt = RefreshToken(
                user_id=user_id,
                token_jti=token_jti,
                expires_at=expires_at,
            )
        self.session.add(rt)
        await self.session.flush()
        return rt
