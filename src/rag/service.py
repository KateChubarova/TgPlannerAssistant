import json
import os
from datetime import datetime

import tzlocal
from openai import OpenAI

from shared.models.embedding_record import EmbeddingRecord
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_text
from shared.nlp.prompts.loader import load_yaml_prompts
from shared.storage.embeddings_repo import search_similar_embeddings
from tools.location_tool import location_tool
from web_search.client import enrich_event_by_location

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")

prompts = load_yaml_prompts("prompt")
client = OpenAI(api_key=OPENAI_TOKEN)

tz = tzlocal.get_localzone()
now = datetime.now(tz).isoformat(timespec="seconds")

system_prompt = prompts["system"].format(
    now=now,
    timezone=tz
)


def build_context_from_rows(records: list[EmbeddingRecord]) -> str:
    """
    Формирует текстовый контекст для RAG-ответа на основе найденных EmbeddingRecord.
    Каждая запись конвертируется в строку с названием календаря, источником,
    объединённым текстом и списком участников.
    """
    parts = []
    for record in records:
        parts.append(
            f"[{record.calendar_name}/{record.source}] "
            f"{record.combined_text} (участники: {record.participants})")

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_location_info(tool_call, messages) -> str:
    """
    Обрабатывает tool-call enrich_event_by_location, вызывает внешний сервис
    для обогащения информации о событии по локации и возвращает финальный ответ модели.
    """
    args = json.loads(tool_call.function.arguments)
    location = args["location"]

    tool_result = enrich_event_by_location(location=location)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": "enrich_event_by_location",
        "content": json.dumps(tool_result, ensure_ascii=False),
    })

    final = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
    )

    return final.choices[0].message.content


def answer_with_rag(user: TgUser, user_query: str) -> str:
    """
    Отвечает на пользовательский запрос с помощью RAG-подхода:
    - строит embedding запроса,
    - ищет похожие записи в базе,
    - формирует контекст,
    - вызывает LLM с возможностью использования инструментов,
    - при необходимости обрабатывает tool-calls.
    """

    query_embedding = embed_text(user_query)
    rows = search_similar_embeddings(user, query_embedding, top_k=5)

    context = build_context_from_rows(rows)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": f"Контекст событий пользователя:\n{context}"},
        {"role": "user", "content": user_query}
    ]

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        tools=[location_tool],
        tool_choice="auto",
    )

    answer = completion.choices[0].message
    messages.append(answer)

    if not answer.tool_calls:
        return answer.content
    else:
        for tool_call in answer.tool_calls:
            fn_name = tool_call.function.name
            if fn_name == "enrich_event_by_location":
                return answer_with_location_info(tool_call, messages)
