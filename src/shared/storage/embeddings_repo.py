import os
from typing import List, Sequence
from sqlalchemy import create_engine, MetaData, Table, text, RowMapping

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, future=True)
meta = MetaData()

tbl = Table("tg_embeddings", meta, autoload_with=engine, schema="public")


def search_similar_embeddings(
        embedding: List[float],
        top_k: int = 5,
) -> Sequence[RowMapping]:
    query = text("""
        SELECT
            id,
            combined_text,
            participants,
            calendar_name,
            updated_at,
            source,
            status
        FROM tg_embeddings
        ORDER BY message <-> CAST(:query_embedding AS vector)
        LIMIT :top_k
    """)

    with engine.connect() as conn:
        rows = conn.execute(
            query,
            {
                "query_embedding": embedding,
                "top_k": top_k,
            },
        ).mappings().all()

    return rows
