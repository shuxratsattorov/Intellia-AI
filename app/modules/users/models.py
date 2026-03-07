from __future__ import annotations
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin
from app.modules.auth.models.auth import UserCredentials


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    credentials: Mapped["UserCredentials"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    preferences: Mapped["UserPreferences"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserPreferences(Base, IDMixin):
    __tablename__ = "user_preferences"

    theme: Mapped[str] = mapped_column(String(8), default="system")  # dark|light|system
    language: Mapped[str | None] = mapped_column(String(12), nullable=True)

    user: Mapped["User"] = relationship(back_populates="preferences")
