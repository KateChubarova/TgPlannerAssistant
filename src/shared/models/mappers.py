from datetime import datetime
from typing import List

from shared.models.calendar_event import CalendarEvent
from shared.models.embedding_record import EmbeddingRecord


def map_event_to_embedding(
        event: CalendarEvent,
        vec: List[float]
) -> EmbeddingRecord:
    return EmbeddingRecord(
        id=event.id,
        participants=event.participants,
        combined_text=event.to_str(),
        calendar_name=event.calendar,
        updated_at=datetime.utcnow(),
        source=event.calendar,
        status=event.status,
        message=vec,
        location=event.location,
        start_ts=datetime.fromisoformat(event.start_ts['dateTime']),
        end_ts=datetime.fromisoformat(event.end_ts['dateTime'])
    )
