"""
Canonical type definitions and mixins for SANGAM entities.
Provides reusable patterns for UUID primary keys, UTC timestamps,
and common column configurations.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid() -> UUID:
    """Generate a new UUID4 identifier."""
    return uuid4()


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    """Mixin providing UUID primary key column."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid,
        comment="UUID primary key",
    )


class TimestampMixin:
    """Mixin providing created_at and updated_at UTC timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        index=True,
        comment="Record creation timestamp (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        comment="Last modification timestamp (UTC)",
    )


class SoftDeleteMixin:
    """Mixin providing soft-delete capability."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        comment="Soft-delete timestamp (NULL = active)",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        index=True,
        comment="Active flag (denormalized for query performance)",
    )
