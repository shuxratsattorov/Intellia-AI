from __future__ import annotations
from sqlalchemy import select
from datetime import datetime, timezone

from app.main import datatime
from app.modules.users.models import User
from app.db.base_repo import AsyncRepository
from app.modules.auth.models.auth import (
    UserCredentials,
    RefreshToken,
    PasswordResetToken,
    EmailVerificationToken
)


class UserRepository(AsyncRepository[User]):
    model = User

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_user(self, email: str, is_active: bool) -> User:
        user = User(
        email=email,
        is_active=is_active,
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


class PasswordResetTokenRepository(AsyncRepository[PasswordResetToken]):
    """Repository for PasswordResetToken entity."""

    model = PasswordResetToken

    async def get_valid_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        """Fetch valid (unused, non-expired) reset token by hash."""
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class EmailVerificationTokenRepository(AsyncRepository[EmailVerificationToken]):
    model = EmailVerificationToken

    # -------------------------
    # CREATE
    # -------------------------

    async def create(
        self,
        user_id: int,
        code_hash: str,
        purpose: str,
        expires_at: datatime,
    ) -> EmailVerificationToken:
        token = EmailVerificationToken(
            user_id=user_id,
            code_hash=code_hash,
            purpose=purpose,
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    # -------------------------
    # GET
    # -------------------------

    async def get_by_id(self, token_id: int) -> Optional[EmailVerificationToken]:
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.id == token_id
            )
        )
        return result.scalar_one_or_none()

    async def get_active_token(
        self,
        user_id: int,
        purpose: str,
    ) -> Optional[EmailVerificationToken]:
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                and_(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.purpose == purpose,
                    EmailVerificationToken.used == False,
                    EmailVerificationToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        code_hash: str,
        purpose: str,
    ) -> Optional[EmailVerificationToken]:
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                and_(
                    EmailVerificationToken.code_hash == code_hash,
                    EmailVerificationToken.purpose == purpose,
                )
            )
        )
        return result.scalar_one_or_none()

    # -------------------------
    # UPDATE
    # -------------------------

    async def mark_as_used(
        self,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:
        token.used = True
        token.used_at = datetime.now(timezone.utc)
        await self.session.flush()
        return token

    async def increment_attempts(
        self,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:
        """Noto'g'ri urinish — attempts ni oshirish"""
        token.attempts += 1
        await self.session.flush()
        return token

    async def set_cooldown(
        self,
        token: EmailVerificationToken,
        cooldown_minutes: int = 5,
    ) -> EmailVerificationToken:
        """Ko'p noto'g'ri urinishdan keyin cooldown o'rnatish"""
        token.cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)
        await self.session.flush()
        return token

    # -------------------------
    # DELETE
    # -------------------------

    async def delete(self, token: EmailVerificationToken) -> None:
        await self.session.delete(token)
        await self.session.flush()

    async def delete_expired(self, user_id: int, purpose: TokenPurpose) -> None:
        """Foydalanuvchining eski tokenlarini o'chirish"""
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                and_(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.purpose == purpose,
                    EmailVerificationToken.expires_at < datetime.now(timezone.utc),
                )
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            await self.session.delete(token)
        await self.session.flush()

    # -------------------------
    # VALIDATION
    # -------------------------

    def is_expired(self, token: EmailVerificationToken) -> bool:
        return token.expires_at < datetime.now(timezone.utc)

    def is_on_cooldown(self, token: EmailVerificationToken) -> bool:
        if token.cooldown_until is None:
            return False
        return token.cooldown_until > datetime.now(timezone.utc)

    def is_max_attempts_reached(
        self,
        token: EmailVerificationToken,
        max_attempts: int = 5,
    ) -> bool:
        return token.attempts >= max_attempts

    def verify_code(
        self,
        token: EmailVerificationToken,
        code: str,
    ) -> bool:
        return token.code_hash == self._hash_code(code)

    # -------------------------
    # PRIVATE
    # -------------------------

    @staticmethod
    def _hash_code(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()
























    async def attempts(self, user_id: int, attempts: int) -> EmailVerificationToken:
        attempts = EmailVerificationToken(
            attempts=attempts
        )
        self.session.add(attempts)
        await self.session.flush()
        return attempts

    async def get_attempts(self, attempts: int)    

    async def create(
        self, 
        token: str, 
        expires_at: datetime, 
        used: bool
    ) -> EmailVerificationToken:
    
        evt = EmailVerificationToken(
            token=token, 
            expires_at=expires_at,  
            used=used
    )
        self.add(evt)
        await self.session.flush()       