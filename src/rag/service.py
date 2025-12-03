import json
import os
from datetime import datetime

import tzlocal
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

from rag.prompts.loader import load_yaml_prompts
from rag.tools.location_tool import location_tool
from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_query
from shared.storage.embeddings_repo import search_similar_embeddings
from sources.web_search.client import enrich_event_by_location

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


def build_context(records: list[Embedding]) -> str:
    parts = []
    for record in records:
        parts.append(
            f"[{record.calendar_name}/{record.source}] "
            f"{record.combined_text} (участники: {record.participants})")

    return "\n".join(parts) if parts else "Нет релевантных записей календаря."


def answer_with_rag(user: TgUser, user_query: str, top_k=5) -> str | None:
    query_embedding = embed_query(user_query)
    rows = search_similar_embeddings(user, query_embedding, top_k=top_k)

    context = build_context(rows)

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


def answer_with_location_info(tool_call: ChatCompletionMessage, messages: [dict]) -> str:
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
