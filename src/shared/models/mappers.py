from datetime import datetime
from typing import List

from shared.models.calendar_event import CalendarEvent
from shared.models.embedding_record import EmbeddingRecord
from shared.models.user import TgUser


def get_date_time(date: dict):
    """
    Преобразует структуру даты из Google Calendar в объект datetime.
    Поддерживает два формата:
    - dateTime: полная дата со временем (например, "2025-01-14T10:00:00Z")
    - date: только дата (например, "2025-01-14")
    """

    if 'dateTime' in date:
        return datetime.fromisoformat(date['dateTime'])
    elif 'date' in date:
        return datetime.fromisoformat(date['date'])


def map_event_to_embedding(
        user: TgUser,
        event: CalendarEvent,
        vec: List[float]
) -> EmbeddingRecord:
    """
    Преобразует объект CalendarEvent в EmbeddingRecord для последующего сохранения в базу.
    Создаёт запись с текстовым представлением события, embedding-вектором,
    метаданными (участники, локация, статус), временными метками и привязкой к пользователю.
        EmbeddingRecord: Готовая запись для индексации и сохранения.
    """

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
        start_ts=get_date_time(event.start_ts),
        end_ts=get_date_time(event.end_ts),
        user_id=user.id
    )
