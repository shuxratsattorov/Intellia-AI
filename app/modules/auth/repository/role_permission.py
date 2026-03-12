from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from app.modules.users.models import User
from app.db.base_repo import AsyncRepository
from app.modules.auth.models.role_permission import (
    Permission,
    Role,
    UserRole,
    RolePermission,
)


class PermissionRepository(AsyncRepository[Permission]):
    model = Permission

    async def get_by_id(self, permission_id: int) -> Permission | None:
        stmt = select(Permission).where(Permission.id == permission_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_names(self, names: list[str]) -> list[Permission]:
        if not names:
            return []

        stmt = select(Permission).where(Permission.name.in_(names))
        result = await self.session.execute(stmt)
        return list[Permission](result.scalars().all())

    async def list_all(self) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.id)
        result = await self.session.execute(stmt)
        return list[Permission](result.scalars().all())

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(Permission.id).where(Permission.name == name).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, name: str) -> Permission:
        permission = Permission(name=name)
        self.session.add(permission)
        await self.session.flush()
        return permission


class RoleRepository(AsyncRepository[Role]):
    model = Role

    async def get_by_id(self, role_id: int) -> Role | None:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Role]:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .order_by(Role.id)
        )
        result = await self.session.execute(stmt)
        return list[Role](result.scalars().unique().all())

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(Role.id).where(Role.name == name).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, name: str) -> Role:
        role = Role(name=name)
        self.session.add(role)
        await self.session.flush()
        return role


class UserRepository(AsyncRepository[User]):
    model = User

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.credentials),
                selectinload(User.preferences),
            )
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.credentials),
                selectinload(User.preferences),
            )
            .where(User.email == email)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, email: str, is_active: bool = True) -> User:
        user = User(
            email=email,
            is_active=is_active,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def list_all(self) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .order_by(User.id)
        )
        result = await self.session.execute(stmt)
        return list[User](result.scalars().unique().all())

    async def has_permission(self, user_id: int, permission_name: str) -> bool:
        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Permission.name == permission_name,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None    


class UserRoleRepository(AsyncRepository[UserRole]):
    model = UserRole

    async def assign_role(self, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(
            user_id=user_id, 
            role_id=role_id
        )
        self.session.add(user_role)
        await self.session.flush()
        return user_role

    async def remove_role(self, user_id: int, role_id: int) -> bool:
        stmt = delete(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, user_id: int, role_id: int) -> bool:
        stmt = (
            select(UserRole.user_id)
            .where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


class RolePermissionRepository(AsyncRepository[RolePermission]):
    model = RolePermission

    async def assign_permission(self, role_id: int, permission_id: int) -> RolePermission:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.session.add(role_permission)
        await self.session.flush()
        return role_permission

    async def remove_permission(self, role_id: int, permission_id: int) -> bool:
        stmt = delete(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, role_id: int, permission_id: int) -> bool:
        stmt = (
            select(RolePermission.role_id)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None










# class RolePermissionRepository(AsyncRepository
#     [Role, UserRole, Permission, RolePermission]
#     ):
#     model = Role, UserRole, Permission, RolePermission

#     async def get_by_name_role(self, name: str) -> Role | None:
#         stmt = select(Role).where(Role.name == name)
#         result = await self.session.execute(stmt)
#         return result.scalar_one_or_none()

#     async def get_by_name_permission(self, name: str) -> Permission | None:
#         stmt = select(Permission).where(Permission.name == name)
#         result = await self.session.execute(stmt)
#         return result.scalar_one_or_none()

#     async def create_role(self, name: str) -> Role:
#         role = Role(name=name)
#         self.session.add(role)
#         await self.session.flush()

#     async def create_permission(self, name: str) -> Permission:
#         permission = Role(name=name)
#         self.session.add(permission)
#         await self.session.flush()

#     async def create_role_permission()


# class UserRoleRepository(AsyncRepository[UserRole]):
#     """Repository for UserRole junction entity."""

#     model = UserRole

#     async def assign_role(self, user_id: int, role_id: int) -> UserRole:
#         """
#         Assign a role to a user.

#         The underlying table includes a non-nullable 'id' column without a database
#         default, so we compute the next id manually to satisfy the constraint.
#         """
#         result = await self.session.execute(
#             select(func.coalesce(func.max(UserRole.id), 0))
#         )
#         next_id = (result.scalar_one() or 0) + 1

#         user_role = UserRole(id=next_id, user_id=user_id, role_id=role_id)
#         self.session.add(user_role)
#         await self.session.flush()
#         return user_role
