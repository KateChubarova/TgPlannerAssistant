from datetime import datetime, date
from typing import List, Iterable

from pgvector import Vector

from shared.models.calendar_event import CalendarEvent
from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_calendar_event


def map_date_time(timestamp: dict) -> date|None:
    """
    Extract a datetime or date value from a timestamp dictionary.

    This function reads a timestamp dictionary containing either a `dateTime`
    or a `date` field and converts it into a Python datetime/date object.

    Args:
        timestamp (dict): A dictionary containing either 'dateTime' or 'date'
            in ISO 8601 string format.

    Return:
        date: A datetime object when 'dateTime' is present, a date object
            when only 'date' is present, or None if neither key exists.
    """
    if 'dateTime' in timestamp:
        return datetime.fromisoformat(timestamp['dateTime'])
    if 'date' in timestamp:
        return datetime.fromisoformat(timestamp['date'])


def map_event_to_embedding(
        user: TgUser,
        event: CalendarEvent,
        vec: Vector
) -> Embedding:
    """
    Convert a calendar event into an Embedding model instance.

    This function takes user information, a calendar event, and an embedding vector,
    and maps them into a unified Embedding object suitable for storage and search.

    Args:
        user (TgUser): The Telegram user who owns the event.
        event (CalendarEvent): The calendar event to be transformed.
        vec (List[float]): The embedding vector representing the event.

    Return:
        Embedding: A fully constructed Embedding object containing event metadata
            and its semantic vector.
    """
    return Embedding(
        id=event.id,
        participants=event.participants,
        combined_text=event.to_str(),
        calendar_name=event.calendar,
        updated_at=datetime.utcnow(),
        source=event.calendar,
        status=event.status,
        message=vec,
        location=event.location,
        start_ts=map_date_time(event.start_ts),
        end_ts=map_date_time(event.end_ts),
        user_id=user.id,
        updated=event.updated
    )


def map_events(user: TgUser, events: Iterable[CalendarEvent]) -> List[Embedding]:
    """
    Convert multiple calendar events into embedding objects.

    This function iterates through a collection of calendar events, embeds each one,
    and returns a list of Embedding model instances.

    Args:
        user (TgUser): The Telegram user to whom the events belong.
        events (Iterable[CalendarEvent]): A collection of calendar events to embed.

    Return:
        List[Embedding]: A list of embedding objects representing the provided events.
    """
    embeddings: List[Embedding] = []
    for event in events:
        embedding = map_event_to_embedding(user, event, embed_calendar_event(event))
        embeddings.append(embedding)
    return embeddings
