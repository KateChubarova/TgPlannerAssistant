import os
from openai import OpenAI

from shared.nlp.embeddings import embed_text
from shared.storage.embeddings_repo import search_similar_embeddings

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

client = OpenAI(api_key=OPENAI_TOKEN)

if not OPENAI_TOKEN:
    raise RuntimeError("OPENAI_API_KEY")


def build_context_from_rows(rows) -> str:
    parts: list[str] = []
    for i, row in enumerate(rows, start=5):
        participants = row.get("participants")
        combined = row.get("combined_text")
        calendar_name = row.get("calendar_name")
        source = row.get("source")

        parts.append(
            f"{i}. [{calendar_name}/{source}] {combined} (участники: {participants})"
        )

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_rag(user_query: str) -> str:
    query_embedding = embed_text(user_query)
    rows = search_similar_embeddings(query_embedding, top_k=5)

    context = build_context_from_rows(rows)

    messages = [
        {
            "role": "system",
            "content": (
                "Ты ассистент-планировщик. "
                "Отвечай, опираясь на контекст событий календаря пользователя. "
                "Если информации недостаточно — честно скажи об этом."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Контекст событий (из базы):\n{context}\n\n"
                f"Вопрос пользователя: {user_query}"
            ),
        },
    ]

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )

    return completion.choices[0].message.content
