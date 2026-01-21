from datetime import date

from pgvector import Vector
from sqlalchemy import and_, select

from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.storage.db import SessionLocal


def search_similar_embeddings(
    user: TgUser,
    embedding: Vector,
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


def search_events_by_date_range(
    user: TgUser,
    start_date: date,
    end_date: date,
    top_k: int = 50,
) -> [Embedding]:
    print(start_date)
    print(end_date)
    stmt = (
        select(Embedding)
        .where(
            and_(
                Embedding.user_id == user.id,
                Embedding.start_ts >= start_date,
                Embedding.start_ts <= end_date,
            )
        )
        .limit(top_k)
    )

    with SessionLocal() as session:
        return session.execute(stmt).scalars().all()
