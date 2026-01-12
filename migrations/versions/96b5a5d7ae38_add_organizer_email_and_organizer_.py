"""add organazier_email and organazier_display name

Revision ID: 96b5a5d7ae38
Revises: a97baafd0810
Create Date: 2026-01-09 14:52:15.607353

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "96b5a5d7ae38"
down_revision: Union[str, Sequence[str], None] = "a97baafd0810"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tg_embeddings",
        sa.Column("organizer_email", sa.String(), nullable=True),
    )
    op.add_column(
        "tg_embeddings",
        sa.Column("organizer_display_name", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tg_embeddings", "organizer_email")
    op.drop_column("tg_embeddings", "organizer_display_name")
