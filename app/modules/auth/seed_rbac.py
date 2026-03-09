from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.repository.role_permission import (
    PermissionRepository, 
    RoleRepository, 
    RolePermissionRepository)


PERMISSIONS = [
    "users:read",
    "users:create",
    "users:update",
    "users:delete",
    "projects:read",
    "projects:create",
    "projects:update",
    "projects:delete",
    "ai:read",
    "ai:create",
    "ai:update",
    "ai:delete",
]

ROLE = {
    "admin": [
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "projects:read",
        "projects:create",
        "projects:update",
        "projects:delete",
        "ai:read",
        "ai:create",
        "ai:update",
        "ai:delete",
    ],
    "user": [
        "users:read",
        "users:update",
        "projects:read",
        "projects:create",
        "projects:update",
        "projects:delete",
        "ai:read",
        "ai:create",
        "ai:update",
        "ai:delete",
    ],
}


class RBACManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.permission_repo = PermissionRepository(session)
        self.role_repo = RoleRepository(session)
        self.role_permission_repo = RolePermissionRepository(session)

    async def seed_all(self) -> dict[str, int]:
        created_permissions = 0
        created_roles = 0
        created_role_permissions = 0

        for permission_name in PERMISSIONS:
            permission = await self.permission_repo.get_by_name(permission_name)
            if not permission:
                await self.permission_repo.create(permission_name)
                created_permissions += 1

        for role_name in ROLE.keys():
            role = await self.role_repo.get_by_name(role_name)
            if not role:
                await self.role_repo.create(role_name)
                created_roles += 1

        for role_name, permission_names in ROLE.items():
            role = await self.role_repo.get_by_name(role_name)
            if not role:
                continue

            permissions = await self.permission_repo.get_by_names(permission_names)

            for permission in permissions:
                exists = await self.role_permission_repo.exists(
                    role_id=role.id,
                    permission_id=permission.id,
                )
                if not exists:
                    await self.role_permission_repo.assign_permission(
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                    created_role_permissions += 1

        await self.session.commit()

        return {
            "created_permissions": created_permissions,
            "created_roles": created_roles,
            "created_role_permissions": created_role_permissions,
        }























# async def get_or_create_permission(session, name: str) -> Permission:
#     stmt = select(Permission).where(Permission.name == name)
#     result = await session.execute(stmt)
#     perm = result.scalar_one_or_none()
#     if perm:
#         return perm
#     perm = Permission(name=name)
#     session.add(perm)
#     await session.flush()
#     return perm


# async def get_or_create_role(session, name: str) -> Role:
#     stmt = select(Role).where(Role.name == name)
#     result = await session.execute(stmt)
#     role = result.scalar_one_or_none()
#     if role:
#         return role
#     role = Role(name=name)
#     session.add(role)
#     await session.flush()
#     return role


# async def seed_permissions_and_roles(session) -> None:
#     try:
#         permission_map: dict[str, Permission] = {}

#         for permission_name in PERMISSIONS:
#             permission = await get_or_create_permission(session, permission_name)
#             permission_map[permission_name] = permission

#         for role_name, permission_names in ROLE.items():
#             role = await get_or_create_role(session, role_name)

#             missing_permissions = [
#                 name for name in permission_names if name not in permission_map
#             ]
#             if missing_permissions:
#                 raise ValueError(
#                     f"Permissions not found for role {role_name}: {missing_permissions}"
#                 )

#             role.permissions = [permission_map[name] for name in permission_names]

#         await session.commit()

#     except Exception:
#         await session.rollback()
#         raise
