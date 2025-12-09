from typing import List

from sqlalchemy import select

from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.storage.db import SessionLocal


def search_similar_embeddings(
    user: TgUser,
    embedding: List[float],
    top_k: int = 5,
) -> [Embedding]:
    stmt = (
        select(Embedding)
        .where(Embedding.user_id == user.id)
        .order_by(
            Embedding.start_ts.asc(),
            Embedding.message.op("<->")(embedding),
        )
        .order_by(Embedding.start_ts.asc())
        .limit(top_k)
    )
    with SessionLocal() as session:
        return session.execute(stmt).scalars().all()
