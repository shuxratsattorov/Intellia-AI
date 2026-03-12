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
