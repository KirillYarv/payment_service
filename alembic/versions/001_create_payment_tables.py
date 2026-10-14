"""Create tariffs, payments and promocodes.

Revision ID: 001
Revises:
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create the three application tables; do not insert any data."""
    op.create_table(
        "tariffs",
        sa.Column("id", sa.SmallInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.CHAR(length=20), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_table(
        "promocodes",
        sa.Column("name", sa.CHAR(length=50), nullable=False),
        sa.Column("discount", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("status", sa.CHAR(length=16), nullable=False),
        sa.Column("tariff_id", sa.SmallInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("discount", sa.BigInteger(), nullable=False),
        sa.Column("schedule", postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column("method", sa.CHAR(length=16), nullable=False),
        sa.Column("installment_months", sa.SmallInteger(), nullable=True),
        sa.Column("email", sa.CHAR(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("idempotency_key", sa.CHAR(length=255), nullable=True),
        sa.ForeignKeyConstraint(["tariff_id"], ["tariffs.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )


def downgrade() -> None:
    """Drop tables in reverse foreign-key order."""
    op.drop_table("payments")
    op.drop_table("promocodes")
    op.drop_table("tariffs")
