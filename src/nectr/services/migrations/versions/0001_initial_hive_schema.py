"""Initial deterministic Hive persistence schema.

Revision ID: 0001_initial_hive_schema
Revises:
Create Date: 2026-11-21 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_hive_schema"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "hive_states",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("collusion_alpha", sa.Float(), nullable=False),
        sa.Column("lineage_gamma", sa.Float(), nullable=False),
        sa.Column("accepted_status_peer_threshold", sa.Integer(), nullable=False),
        sa.Column("comb_reserve", sa.Float(), nullable=False),
        sa.Column("total_minted_supply", sa.Float(), nullable=False),
        sa.Column("current_epoch", sa.Integer(), nullable=False),
        sa.Column("mempool_json", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("hive_id"),
    )
    op.create_table(
        "bee_accounts",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("bee_id", sa.String(), nullable=False),
        sa.Column("home_hive_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("raw_pollen_balance", sa.Float(), nullable=False),
        sa.Column("liquid_nectr_balance", sa.Float(), nullable=False),
        sa.Column("certified_subjects_json", sa.String(), nullable=False),
        sa.Column("accepted_in_hives_json", sa.String(), nullable=False),
        sa.Column("distinct_peers_tutored_json", sa.String(), nullable=False),
        sa.Column("royal_jelly_earned", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "bee_id"),
    )
    op.create_table(
        "service_barter_sessions",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("tutor_id", sa.String(), nullable=False),
        sa.Column("learner_id", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("escrowed_amount", sa.Float(), nullable=False),
        sa.Column("token_state", sa.String(), nullable=False),
        sa.Column("reciprocal_subject_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("learner_attestation_score", sa.Float(), nullable=False),
        sa.Column("tutor_comprehension_hash", sa.String(), nullable=False),
        sa.Column("effective_weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "session_id"),
    )
    op.create_table(
        "pairwise_counts",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("bee_a", sa.String(), nullable=False),
        sa.Column("bee_b", sa.String(), nullable=False),
        sa.Column("tx_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "bee_a", "bee_b"),
    )
    op.create_table(
        "subject_lineage",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("learner_id", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=False),
        sa.Column("tutors_json", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "learner_id", "subject_id"),
    )
    op.create_table(
        "tutor_effectiveness",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("tutor_id", sa.String(), nullable=False),
        sa.Column("effectiveness", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "tutor_id"),
    )
    op.create_table(
        "settled_tx_logs",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("seq_index", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("tx_json", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "seq_index"),
    )
    op.create_table(
        "hive_blocks",
        sa.Column("hive_id", sa.String(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("block_hash", sa.String(), nullable=False),
        sa.Column("prev_hash", sa.String(), nullable=False),
        sa.Column("merkle_root", sa.String(), nullable=False),
        sa.Column("knowledge_graph_root", sa.String(), nullable=False),
        sa.Column("timestamp", sa.Float(), nullable=False),
        sa.Column("block_json", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["hive_id"], ["hive_states.hive_id"]),
        sa.PrimaryKeyConstraint("hive_id", "height"),
    )


def downgrade() -> None:
    op.drop_table("hive_blocks")
    op.drop_table("settled_tx_logs")
    op.drop_table("tutor_effectiveness")
    op.drop_table("subject_lineage")
    op.drop_table("pairwise_counts")
    op.drop_table("service_barter_sessions")
    op.drop_table("bee_accounts")
    op.drop_table("hive_states")
