from datetime import date, datetime
from typing import List

from pgvector import Vector

from shared.models.calendar_event import CalendarEvent
from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_calendar_event


def map_date_time(timestamp: dict) -> date | None:
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
    if "dateTime" in timestamp:
        return datetime.fromisoformat(timestamp["dateTime"])
    elif "date" in timestamp:
        return datetime.fromisoformat(timestamp["date"])


def map_event_to_embedding(
    user: TgUser, event: CalendarEvent, vec: Vector
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
        id=event.event_id + str(user.id),
        event_id=event.event_id,
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
        updated=event.updated,
    )


def map_events(
    user: TgUser, events: [CalendarEvent], progress_callback=None
) -> List[Embedding]:
    total = len(events) or 1

    """
    Convert multiple calendar events into embedding objects.

    This function iterates through a collection of calendar events, embeds each one,
    and returns a list of Embedding model instances.

    Args:
        user (TgUser): The Telegram user to whom the events belong.
        events (Iterable[CalendarEvent]): A collection of calendar events to embed.
        progress_callback (callable, optional):
            A function that will be called during the heavy processing step
            (embedding generation) to report progress. The callback must accept
            two integer arguments:

                progress_callback(current: int, total: int)

            where:
                * current — number of processed items so far
                * total   — total number of items to process

            This can be used to update a loading indicator in a Telegram bot
            (for example, showing percentage of completion). If None, progress
            updates are not reported.

    Return:
        List[Embedding]: A list of embedding objects representing the provided events.
    """
    embeddings: List[Embedding] = []
    for idx, event in enumerate(events, start=1):
        embedding = map_event_to_embedding(user, event, embed_calendar_event(event))
        embeddings.append(embedding)

        if progress_callback:
            progress_callback(idx, total)

    return embeddings
