from typing import List
from sqlalchemy import select

from shared.db import SessionLocal
from shared.models.embedding_record import EmbeddingRecord
from shared.models.user import TgUser


def search_similar_embeddings(
        user: TgUser,
        embedding: List[float],
        top_k: int = 5,
) -> list[EmbeddingRecord]:
    stmt = (
        select(EmbeddingRecord)
        .where(EmbeddingRecord.user_id == user.id)
        .order_by(EmbeddingRecord.message.op("<->")(embedding))
        .limit(top_k)
    )
    with SessionLocal() as session:
        return session.execute(stmt).scalars().all()
