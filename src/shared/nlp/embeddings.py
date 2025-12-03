import os
from typing import List
from openai import OpenAI
from shared.models.calendar_event import CalendarEvent

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

client = OpenAI(api_key=OPENAI_TOKEN)


def embed_calendar_event(event: CalendarEvent) -> List[float]:
    """
    Embed a calendar event into a vector representation.

    This function converts the given calendar event into a text form and sends it
    to the embedding model to generate a numerical vector used for semantic search.

    Args:
        event (CalendarEvent): The calendar event object to be encoded into an embedding.

    Return:
        List[float]: A vector representation (embedding) of the calendar event.
    """
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=event.to_str())
    return resp.data[0].embedding


def embed_query(query: str) -> List[float]:
    """
    Embed a user query into a vector representation.

    This function sends a raw text query to the embedding model and retrieves
    its corresponding semantic vector, which is used for similarity search.

    Args:
        query (str): The text query that should be converted into an embedding vector.

    Return:
        List[float]: A vector representation (embedding) of the input query.
    """
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return resp.data[0].embedding
