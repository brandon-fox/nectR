"""Add bee_keys table for Ed25519 public key and monotonic nonce persistence.

Revision ID: 0003_bee_keys_registry
Revises: 0002_micro_unit_accounting
Create Date: 2026-11-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_bee_keys_registry"
down_revision: str | Sequence[str] | None = "0002_micro_unit_accounting"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bee_keys",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("bee_id", sa.String(), nullable=False),
        sa.Column("public_key", sa.String(), nullable=False),
        sa.Column("last_nonce", sa.BigInteger(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "bee_id"),
    )


def downgrade() -> None:
    op.drop_table("bee_keys")
