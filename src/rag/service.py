import os
from datetime import datetime

import tzlocal
from openai import OpenAI

from shared.models.user import TgUser
from shared.nlp.embeddings import embed_text
from shared.nlp.prompts.loader import load_yaml_prompts
from shared.storage.embeddings_repo import search_similar_embeddings
from web_search.client import enrich_event_by_location, format_location_info

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

prompts = load_yaml_prompts("planner")
client = OpenAI(api_key=OPENAI_TOKEN)

tz = tzlocal.get_localzone()
now = datetime.now(tz).isoformat(timespec="seconds")

system_prompt = prompts["system"].format(
    now=now,
    timezone=tz
)


def build_context_from_rows(event) -> str:
    parts: list[str] = \
        [f"[{event.calendar_name}/{event.source}] "
         f"{event.combined_text} (участники: {event.participants})"]

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_rag(user: TgUser, user_query: str) -> str:
    query_embedding = embed_text(user_query)
    rows = search_similar_embeddings(user, query_embedding, top_k=5)

    main_event = rows[0]
    context = build_context_from_rows(main_event)

    location_info_text = ""
    if main_event.location:
        web_results = enrich_event_by_location(main_event)
        location_info_text = format_location_info(web_results)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": f"Контекст событий пользователя:\n{context}"},
    ]

    if location_info_text:
        messages.append({
            "role": "assistant",
            "content": f"Дополнительная информация о месте события:\n{location_info_text}"
        })

    messages.append({"role": "user", "content": user_query})

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )

    return completion.choices[0].message.content

