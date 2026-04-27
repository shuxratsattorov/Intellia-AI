from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Index,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.users.models import User
from app.db.base import Base, IDMixin, TimestampMixin


class UserCredentials(Base):
    __tablename__ = "user_credentials"

    password_hash: Mapped[str] = mapped_column(String(256))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    user: Mapped["User"] = relationship("User", back_populates="credentials")


class OAuthAccount(Base, IDMixin, TimestampMixin):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        Index("ix_oauth_user_provider", "user_id", "provider"))

    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(128), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user: Mapped["User"] = relationship()


class RefreshToken(Base, IDMixin):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String(256))
    jti: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user: Mapped["User"] = relationship()