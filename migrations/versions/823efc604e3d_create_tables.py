"""create tables

Revision ID: 823efc604e3d
Revises: 016f06669a0e
Create Date: 2025-12-08 22:03:50.735384

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "823efc604e3d"
down_revision: Union[str, Sequence[str], None] = "016f06669a0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ----- tg_users -----
    op.create_table(
        "tg_users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("google_access_token", sa.Text(), nullable=True),
        sa.Column("google_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expiry", sa.TIMESTAMP(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ----- tg_embeddings -----
    op.create_table(
        "tg_embeddings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_id", sa.String(), nullable=True),
        sa.Column("participants", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("combined_text", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("message", Vector(), nullable=True),  # VECTOR / Vector
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("end_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("start_ts", sa.TIMESTAMP(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
    )


def downgrade():
    op.drop_table("tg_embeddings")
    op.drop_table("tg_users")
