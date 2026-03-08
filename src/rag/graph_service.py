from datetime import datetime

from rag.graph.graph import graph
from rag.prompts.loader import load_yaml_prompts
from shared.models import TgUser
from shared.models.embedding import Embedding
from shared.nlp.embeddings import embed_query
from shared.storage.embeddings_repo import search_similar_embeddings

prompts = load_yaml_prompts("system_prompt")


def build_calendar_context(records: list[Embedding]) -> str:
    """
    Build a textual context from a list of calendar embeddings.

    This function formats each embedding record into a human-readable string
    containing the calendar name, source, combined text, and participants,
    then joins them into a single context block.

    Args:
        records (list[Embedding]): A list of embedding records representing calendar events.

    Return:
        str: A formatted context string built from the records, or a fallback
            message if no relevant calendar entries are available.
    """
    parts = []
    for record in records:
        parts.append(f"{record.combined_text}")

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_rag(
    user: TgUser,
    user_query: str,
    embed_fn=embed_query,
    search_fn=search_similar_embeddings,
    top_k=5,
):
    query_embedding = embed_fn(user_query)
    rows = search_fn(user, query_embedding, top_k=top_k)

    calendar_context = build_calendar_context(rows)

    system_prompt = prompts["system"].format(
        now=datetime.now(),
        timezone=datetime.now().astimezone().tzinfo,
        calendar_context=calendar_context,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]

    result = graph.invoke(
        {"messages": messages},
        config={
            "metadata": {
                "user_id": str(user.id),
                "top_k": top_k,
                "prompt_name": "planner_system_prompt",
                "prompt_version": prompts["version"],
                "retrieved_docs_count": len(rows),
            },
        },
    )

    return result["messages"][-1].content
