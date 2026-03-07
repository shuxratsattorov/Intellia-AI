from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.auth.models.role import Role
from app.modules.auth.models.permission import Permission
from app.modules.users.models import User
from app.core.security import hash_password

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

ROLE_MAP = {
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
    permission = db.execute(
        select(Permission).where(Permission.name == name)
    ).scalar_one_or_none()

    if permission:
        return permission

    permission = Permission(name=name)
    db.add(permission)
    db.flush()
    return permission


def get_or_create_role(db, name: str) -> Role:
    role = db.execute(
        select(Role).where(Role.name == name)
    ).scalar_one_or_none()

    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.flush()
    return role


def get_or_create_admin_user(db) -> User:
    user = db.execute(
        select(User).where(User.email == "admin@example.com")
    ).scalar_one_or_none()

    if user:
        return user

    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Admin123!"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.flush()
    return user


def main():
    db = SessionLocal()
    try:
        permissions_map: dict[str, Permission] = {}

        for name in PERMISSIONS:
            permissions_map[name] = get_or_create_permission(db, name)

        for role_name, permission_names in ROLE_MAP.items():
            role = get_or_create_role(db, role_name)

            existing = {perm.name for perm in role.permissions}
            for permission_name in permission_names:
                if permission_name not in existing:
                    role.permissions.append(permissions_map[permission_name])

        admin_user = get_or_create_admin_user(db)
        admin_role = db.execute(
            select(Role).where(Role.name == "admin")
        ).scalar_one()

        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)

        db.commit()
        print("RBAC seeded successfully")
        print("admin@example.com / Admin123!")

    finally:
        db.close()


if __name__ == "__main__":
    main()


from fastapi import FastAPI

app = FastAPI(title="Production FastAPI Auth")

@app.get("/")
def root():
    return {"message": "ok"}    