from sqlalchemy import select

from app.modules.auth.models.role import Role
from app.modules.auth.models.permission import Permission


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


def get_or_create_permission(db, name: str) -> Permission:
    smpt = db.execute(
        select(Permission).where(Permission.name == name)
    ).scalar_one_or_none()

    if smpt:
        return smpt

    smpt = Permission(name=name)
    db.add(smpt)
    db.flush()
    return smpt


def get_or_create_role(db, name: str) -> Role:
    smpt = db.execute(
        select(Role).where(Role.name == name)
    ).scalar_one_or_none()

    if smpt:
        return smpt

    smpt = Role(name=name)
    db.add(smpt)
    db.flush()
    return smpt



def seed_permissions_and_roles(db: Session) -> None:
    try:
        permission_map: dict[str, Permission] = {}

        for permission_name in PERMISSIONS:
            permission = get_or_create_permission(db, permission_name)
            permission_map[permission_name] = permission

        for role_name, permission_names in ROLE.items():
            role = get_or_create_role(db, role_name)

            missing_permissions = [
                name for name in permission_names if name not in permission_map
            ]
            if missing_permissions:
                raise ValueError(
                    f"{role_name} role uchun topilmadi: {missing_permissions}"
                )

            role.permissions = [permission_map[name] for name in permission_names]

        db.commit()

    except Exception:
        db.rollback()
        raise
