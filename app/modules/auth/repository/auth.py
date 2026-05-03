from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, update, exists

from app.modules.users.models import User
from app.db.base_repo import AsyncRepository
from app.modules.auth.models.rbac import Role, UserRole, RolePermission
from app.modules.auth.models.auth import RefreshToken, UserCredentials


class UserRepository(AsyncRepository[User]):
    model = User

    async def exists_by_email(self, email: str, is_verified: bool) -> bool:
        stmt = select(
            exists().where(
                User.email == email,
                User.is_verified == is_verified
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def exisit_password_by_email(self, email: str) -> str:
        stmt = select(UserCredentials.password_hash
            ).join(User, User.id == UserCredentials.user_id
            ).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar() 

    async def get_user_by_email(self, email: str) -> int | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_user(self, email: str, is_active: bool, is_verified: bool) -> User:
        user = User(
            email=email,
            is_active=is_active,
            is_verified=is_verified
        )
        self.session.add(user)
        # await self.session.flush()
        self.session.commit()
        return user

    async def set_verified(self, email: str) -> str:
        stmt = update(User
            ).where(User.email == email
            ).values(is_verified=True)
        self.session.execute(stmt)

        return stmt

    async def get_current_roles_by_user_id(self, user_id: int) -> list[Role]:
        stmt = select(Role
            ).join(Role.users
            ).where(UserRole.user_id == user_id)
        
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

        
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


class JWTTokenRepository(AsyncRepository[RefreshToken]):
    model = RefreshToken

    async def jti_exists(self, user_id: int, token: str, jti: str) -> bool:
        stmt = select(RefreshToken.jti
        ).exists().where(
            RefreshToken.user_id == user_id, 
            RefreshToken.token == token, 
            RefreshToken.jti == jti
        )
        result = await self.session.execute(stmt)

        return result.scalar() 

    async def create_refresh_token(self, user_id: int, token: str) -> RefreshToken:  
        stmt = RefreshToken(user_id=user_id,token=token)
        self.session.add(stmt)
        await self.session.flush()

        return stmt

    async def revoke_token(self, user_id: int, token: str, jti: str) -> str:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.token == token)
            .values(jti=jti, revoked_at=datetime.utcnow())
        )
        await self.session.execute(stmt)

        return stmt
