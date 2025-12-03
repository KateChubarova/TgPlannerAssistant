from datetime import datetime, date
from typing import List, Iterable

from shared.models.calendar_event import CalendarEvent
from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_calendar_event


def get_date_time(timestamp: dict) -> date | None:
    if 'dateTime' in timestamp:
        return datetime.fromisoformat(timestamp['dateTime'])
    elif 'date' in timestamp:
        return datetime.fromisoformat(timestamp['date'])


def map_event_to_embedding(
        user: TgUser,
        event: CalendarEvent,
        vec: List[float]
) -> Embedding:
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
        start_ts=get_date_time(event.start_ts),
        end_ts=get_date_time(event.end_ts),
        user_id=user.id
    )


def map_events(user: TgUser, events: Iterable[CalendarEvent]) -> List[Embedding]:
    embeddings: List[Embedding] = []
    for event in events:
        embedding = map_event_to_embedding(user, event, embed_calendar_event(event))
        embeddings.append(embedding)
    return embeddings
