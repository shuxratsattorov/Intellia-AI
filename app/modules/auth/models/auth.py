from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    null,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.users.models import User
from app.db.base import Base, IDMixin, TimestampMixin


class UserCredentials(Base):
    __tablename__ = "user_credentials"

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="credentials")


class PasswordResetToken(Base, IDMixin, TimestampMixin):
    __tablename__ = "password_reset_tokens"

    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship()


class OAuthAccount(Base, IDMixin, TimestampMixin):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        Index("ix_oauth_user_provider", "user_id", "provider"),
    )

    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(128), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship()


class RefreshToken(Base, IDMixin):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_user_active", "user_id", "revoked_at"),
    )

    token_jti: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    ip: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    user_agent: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship()


class EmailVerificationToken(Base, IDMixin):
    __tablename__ = "email_verification_tokens"

    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    user: Mapped["User"] = relationship()
