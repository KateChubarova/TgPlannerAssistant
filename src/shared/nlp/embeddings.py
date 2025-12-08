import os
from openai import OpenAI
from pgvector import Vector

from shared.models.calendar_event import CalendarEvent

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

client = OpenAI(api_key=OPENAI_TOKEN)


def embed_calendar_event(event: CalendarEvent) -> Vector:
    """
    Embed a calendar event into a vector representation.

    This function converts the given calendar event into a text form and sends it
    to the embedding model to generate a numerical vector used for semantic search.

    Args:
        event (CalendarEvent): The calendar event object to be encoded into an embedding.

    Return:
        Vector: A vector representation (embedding) of the calendar event.
    """
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=event.to_str())
    return Vector(resp.data[0].embedding)


def embed_query(query: str) -> Vector:
    """
    Embed a user query into a vector representation.

    This function sends a raw text query to the embedding model and retrieves
    its corresponding semantic vector, which is used for similarity search.

    Args:
        query (str): The text query that should be converted into an embedding vector.

    Return:
        Vector: A vector representation (embedding) of the input query.
    """
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return Vector(resp.data[0].embedding)
