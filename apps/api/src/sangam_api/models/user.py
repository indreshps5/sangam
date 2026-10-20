"""
User and Role models — authentication and authorization entities.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sangam_api.core.database import Base
from sangam_api.core.types import UUIDPrimaryKeyMixin, TimestampMixin


# Many-to-many association table for User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    System role for access control.

    Canonical fields:
    - name: Role name (e.g., "admin", "operator")
    - description: Human-readable description
    - permissions: JSON list of permission strings
    - is_system: Whether this is a built-in system role (cannot be deleted)
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    permissions: Mapped[str | None] = mapped_column(String(2000), nullable=True, comment="JSON array of permission strings")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment="System roles cannot be deleted")

    # Relationships
    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates="roles", lazy="selectin"
    )


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    System user for authentication and authorization.

    Canonical fields:
    - email: Unique email address (login identifier)
    - username: Unique display name
    - hashed_password: Bcrypt-hashed password (never stored in plain text)
    - full_name: Human-readable name
    - is_active: Account active flag
    - is_verified: Email verified flag
    - last_login_at: Last successful login timestamp
    - preferred_timezone: User's timezone for display
    - preferred_language: UI language preference
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    preferred_timezone: Mapped[str | None] = mapped_column(String(50), nullable=True, default="UTC")
    preferred_language: Mapped[str | None] = mapped_column(String(10), nullable=True, default="en")

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles, back_populates="users", lazy="selectin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user", lazy="selectin"
    )
