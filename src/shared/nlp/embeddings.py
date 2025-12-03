import os
from typing import List
from openai import OpenAI
from shared.models.calendar_event import CalendarEvent

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

client = OpenAI(api_key=OPENAI_TOKEN)


def embed_calendar_event(event: CalendarEvent) -> List[float]:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=event.to_str())
    return resp.data[0].embedding


def embed_query(query: str) -> List[float]:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return resp.data[0].embedding
