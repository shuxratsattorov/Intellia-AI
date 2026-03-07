from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin


class Permission(Base, IDMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )