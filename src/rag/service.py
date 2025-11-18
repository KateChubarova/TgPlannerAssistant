import os
from datetime import datetime

import tzlocal
from openai import OpenAI

from shared.nlp.embeddings import embed_text
from shared.nlp.prompts.loader import load_yaml_prompts
from shared.storage.embeddings_repo import search_similar_embeddings

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

prompts = load_yaml_prompts("planner")
client = OpenAI(api_key=OPENAI_TOKEN)

tz = tzlocal.get_localzone()
now = datetime.now(tz).isoformat(timespec="seconds")

system_prompt = prompts["system"].format(
    now=now,
    timezone="Europe/Warsaw",
)

if not OPENAI_TOKEN:
    raise RuntimeError("OPENAI_API_KEY")


def build_context_from_rows(events) -> str:
    parts: list[str] = []
    for i, event in enumerate(events, start=5):
        participants = event.participants
        combined = event.combined_text
        calendar_name = event.calendar_name
        source = event.source

        parts.append(
            f"{i}. [{calendar_name}/{source}] {combined} (участники: {participants})"
        )

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_rag(user_query: str) -> str:
    query_embedding = embed_text(user_query)
    rows = search_similar_embeddings(query_embedding, top_k=5)

    context = build_context_from_rows(rows)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompts["user_template"].format(
            context=context,
            user_query=user_query
        )},
    ]

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )

    return completion.choices[0].message.content
