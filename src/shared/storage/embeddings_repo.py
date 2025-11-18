from typing import List
from sqlalchemy import text, select, bindparam

from shared.db import engine, tbl
from shared.models.embedding_record import EmbeddingRecord


def search_similar_embeddings(
        embedding: List[float],
        top_k: int = 5,
) -> list[EmbeddingRecord]:
    query = (
        select(tbl)
        .order_by(text("message <-> CAST(:query_embedding AS vector)"))
        .limit(bindparam("top_k"))
    )

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {
                "query_embedding": embedding,
                "top_k": top_k,
            },
        )
        rows = result.mappings().all()

    records = [EmbeddingRecord(**row) for row in rows]

    return records
