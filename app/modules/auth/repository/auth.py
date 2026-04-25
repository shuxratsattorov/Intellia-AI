from __future__ import annotations
import smtpd
from tkinter import NO
from typing import Optional
from unittest import result
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
    model = RefreshToken

    async def get_jti(self, user_id: int, token: str) -> str:
        stmt = select(RefreshToken.token_jti
        ).where(RefreshToken.user_id ==user_id, RefreshToken.token == token)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_valid_by_jti(self, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_jti == jti,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_by_jti(self, jti: str) -> bool:
        token = await self.get_by_jti(jti)
        if token is None:
            return False
        token.revoked_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
        return True

    async def get_revoke_jti(self, jti: str) -> bool:
        stmt = select(RefreshToken.jti).where(RefreshToken.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None    

    async def get_active_token(self, token: str) -> str | None:
        stmt = select(RefreshToken.token
        ).where(RefreshToken.token == token, RefreshToken.jti.is_(None))  
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none

    async def revoke_jti(self, jti: str) -> RefreshToken:
        stmt = RefreshToken(jti=jti)  
        self.session.add(stmt)
        await self.session.flush()
        return stmt  

    async def create_refresh_token(self, token: str) -> RefreshToken:  
        refresh_token = RefreshToken(
                token=token,
            )
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token
