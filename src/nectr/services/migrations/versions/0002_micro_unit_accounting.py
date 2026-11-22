"""Add exact integer micro-unit accounting columns for lossless supply conservation.

Revision ID: 0002_micro_unit_accounting
Revises: 0001_initial_hive_schema
Create Date: 2026-11-22 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_micro_unit_accounting"
down_revision: str | Sequence[str] | None = "0001_initial_hive_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "hive_states",
        sa.Column("comb_reserve_units", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "hive_states",
        sa.Column(
            "total_minted_supply_units",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "bee_accounts",
        sa.Column("raw_pollen_units", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "bee_accounts",
        sa.Column("liquid_nectr_units", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "bee_accounts",
        sa.Column("royal_jelly_units", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "service_barter_sessions",
        sa.Column("escrowed_units", sa.BigInteger(), nullable=False, server_default="0"),
    )

    op.execute(
        "UPDATE hive_states SET "
        "comb_reserve_units = CAST(ROUND(comb_reserve * 1000000) AS BIGINT), "
        "total_minted_supply_units = CAST(ROUND(total_minted_supply * 1000000) AS BIGINT)"
    )
    op.execute(
        "UPDATE bee_accounts SET "
        "raw_pollen_units = CAST(ROUND(raw_pollen_balance * 1000000) AS BIGINT), "
        "liquid_nectr_units = CAST(ROUND(liquid_nectr_balance * 1000000) AS BIGINT), "
        "royal_jelly_units = CAST(ROUND(royal_jelly_earned * 1000000) AS BIGINT)"
    )
    op.execute(
        "UPDATE service_barter_sessions SET "
        "escrowed_units = CAST(ROUND(escrowed_amount * 1000000) AS BIGINT)"
    )


def downgrade() -> None:
    op.drop_column("service_barter_sessions", "escrowed_units")
    op.drop_column("bee_accounts", "royal_jelly_units")
    op.drop_column("bee_accounts", "liquid_nectr_units")
    op.drop_column("bee_accounts", "raw_pollen_units")
    op.drop_column("hive_states", "total_minted_supply_units")
    op.drop_column("hive_states", "comb_reserve_units")
