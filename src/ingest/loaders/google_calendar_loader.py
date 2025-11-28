from typing import Iterable, List

from ingest.providers.google_calendar import fetch_events
from sqlalchemy import select, delete

from shared.db import SessionLocal
from shared.models.calendar_event import CalendarEvent
from shared.models.embedding_record import EmbeddingRecord
from shared.models.mappers import map_event_to_embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_calendar_event


#
def rows_from_events(user: TgUser, events: Iterable[CalendarEvent]) -> List[EmbeddingRecord]:
    rows: List[EmbeddingRecord] = []
    for ev in events:
        embedding_record = map_event_to_embedding(user, ev, embed_calendar_event(ev))
        rows.append(embedding_record)
    return rows


def load_all_events(user: TgUser) -> {int}:
    events = fetch_events(user)
    batch = rows_from_events(user, events)
    if not batch:
        raise ValueError("Календарь пуст или не удалось извлечь события")

    incoming_ids = {event.id for event in batch}

    with SessionLocal() as session:
        existing_ids = set(
            session.scalars(
                select(EmbeddingRecord.id)
                .where(EmbeddingRecord.user_id == user.id)
            )
        )

        to_insert = [row for row in batch if row.id not in existing_ids]
        to_update = [row for row in batch if row.id in existing_ids]
        to_delete = existing_ids - incoming_ids

        if to_insert:
            session.add_all(to_insert)

        if to_update:
            for update in to_update:
                session.merge(update)

        if to_delete:
            session.execute(
                delete(EmbeddingRecord)
                .where(EmbeddingRecord.id.in_(to_delete))
            )
        session.commit()

    return len(to_insert), len(to_update), len(to_delete)
