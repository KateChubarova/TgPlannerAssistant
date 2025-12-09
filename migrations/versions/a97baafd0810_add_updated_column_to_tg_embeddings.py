"""add updated column to tg_embeddings

Revision ID: a97baafd0810
Revises: 823efc604e3d
Create Date: 2025-12-09 12:29:02.238210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a97baafd0810'
down_revision: Union[str, Sequence[str], None] = '823efc604e3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tg_embeddings",
        sa.Column("updated", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tg_embeddings", "updated")
