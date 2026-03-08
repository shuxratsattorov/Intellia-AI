from sqlalchemy import select

from app.modules.users.models import User
from app.db.base_repo import AsyncRepository
from app.modules.auth.models.auth import UserCredentials
from app.modules.auth.models.permission import Permission
from app.modules.auth.models.role import RolePermission, UserRole, Role


class RegisterRepository(AsyncRepository[User, Role, UserCredentials]):
    model = User, Role, UserCredentials

    async def create_user(
        self, 
        email: str, 
        password_hash: str
    ) -> User:
        
        user = User(
            email=email,
            is_active=True,
            roles=[role],
        )

        role = Role(
            name="user",
            user=user
        )

        credentials = UserCredentials(
            password_hash=password_hash,
            user=user,
        )

        self.session.add(user)
        self.session.add(role)
        self.session.add(credentials)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def existing_user(self, email: str) -> bool:
        await self.session.scalar(select(User).where(User.email == email))
        return

    async def create_user(self, email: str, password: str) -> User:
        user = User(
            email=email,
            password=password,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def default_role_assign(self, role: str):
        pass


class RoleAndPermissionRepository(AsyncRepository):
    table = Permission, Role, UserRole, RolePermission


    async def get_permission(self, name: str) -> Permission:
        smpt = await self.execute(
            select(Permission).where(Permission.name == name)
        )
        return smpt.scalar_one_or_none()
    
    async def create_permission(self, name: str) -> Permission:

        smpt = Permission(name=name)
        self.add(smpt)
        await self.flush()
        return smpt

    async def get_role(self, name: str) -> Role:
        smpt = await self.execute(
            select(Role).where(Role.name == name)
        )
        return smpt.scalar_one_or_none()


    async def create_role(self, name: str) -> Role:
        smpt = Role(name=name)
        self.add(smpt)
        await self.flush()
        return smpt


async def get_role_and_permission_repo() -> RoleAndPermissionRepository:
    return RoleAndPermissionRepository()
