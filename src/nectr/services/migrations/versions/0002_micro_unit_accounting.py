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

    conn = op.get_bind()
    hive_rows = conn.execute(
        sa.text("SELECT hive_id, comb_reserve_units, total_minted_supply_units FROM hive_states")
    ).fetchall()
    for hive_id, comb_units, supply_units in hive_rows:
        acct_sum = conn.execute(
            sa.text(
                "SELECT COALESCE(SUM(raw_pollen_units + liquid_nectr_units), 0) "
                "FROM bee_accounts WHERE hive_id = :hid"
            ),
            {"hid": hive_id},
        ).scalar_one()
        escrow_sum = conn.execute(
            sa.text(
                "SELECT COALESCE(SUM(escrowed_units), 0) "
                "FROM service_barter_sessions "
                "WHERE hive_id = :hid AND status = 'INTENT_ESCROWED'"
            ),
            {"hid": hive_id},
        ).scalar_one()
        residual = int(supply_units) - (int(comb_units) + int(acct_sum) + int(escrow_sum))
        if residual == 0:
            continue
        if abs(residual) > 100:
            raise ValueError(
                f"Cannot migrate hive '{hive_id}' to micro-units: "
                f"supply drift {residual} exceeds legacy 1e-4 tolerance (100 micro-units)."
            )
        new_comb = int(comb_units) + residual
        if new_comb >= 0:
            conn.execute(
                sa.text(
                    "UPDATE hive_states SET comb_reserve_units = :comb, "
                    "comb_reserve = :comb_f WHERE hive_id = :hid"
                ),
                {"comb": new_comb, "comb_f": new_comb / 1_000_000, "hid": hive_id},
            )
        else:
            new_supply = int(supply_units) - residual
            conn.execute(
                sa.text(
                    "UPDATE hive_states SET total_minted_supply_units = :sup, "
                    "total_minted_supply = :sup_f WHERE hive_id = :hid"
                ),
                {"sup": new_supply, "sup_f": new_supply / 1_000_000, "hid": hive_id},
            )


def downgrade() -> None:
    op.drop_column("service_barter_sessions", "escrowed_units")
    op.drop_column("bee_accounts", "royal_jelly_units")
    op.drop_column("bee_accounts", "liquid_nectr_units")
    op.drop_column("bee_accounts", "raw_pollen_units")
    op.drop_column("hive_states", "total_minted_supply_units")
    op.drop_column("hive_states", "comb_reserve_units")
