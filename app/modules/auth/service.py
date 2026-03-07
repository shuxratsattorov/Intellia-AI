from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.models.role import Role


class RegisterService(Exception):
    pass


def register_user(db: Session, *, email: str, password: str) -> User:
    existing_user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        raise RegistrationError("A user with this email already exists")

    default_role = db.execute(
        select(Role).where(Role.name == "user")
    ).scalar_one_or_none()

    if not default_role:
        raise RegistrationError("Default role 'user' is not configured")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
    )

    db.add(user)
    db.flush()

    user.roles.append(default_role)

    db.commit()
    db.refresh(user)

    return user