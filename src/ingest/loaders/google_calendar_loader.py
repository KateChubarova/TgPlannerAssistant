from typing import Iterable, Dict, Any, List

from requests import Session

from ingest.providers.google_calendar import fetch_events
from sqlalchemy import select, insert, update, delete

from shared.db import engine, tbl
from shared.models.calendar_event import CalendarEvent
from shared.models.mappers import map_event_to_embedding
from shared.models.user import TgUser
from shared.nlp.embeddings import embed_calendar_event


def rows_from_events(user: TgUser, events: Iterable[CalendarEvent]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ev in events:
        embedding_record = map_event_to_embedding(user, ev, embed_calendar_event(ev))
        rows.append(embedding_record.to_dict())
    return rows


def load_all_events(session: Session, user: TgUser) -> {int}:
    events = fetch_events(session, user)
    batch = rows_from_events(user, events)
    if not batch:
        raise ValueError("Календарь пуст или не удалось извлечь события")

    incoming_ids = {row["id"] for row in batch}

    for row in batch:
        row["user_id"] = user.id

    with engine.begin() as conn:
        existing_ids = {
            row[0]
            for row in conn.execute(
                select(tbl.c.id).where(tbl.c.user_id == user.id)
            )
        }

        to_insert = [row for row in batch if row["id"] not in existing_ids]
        to_update = [row for row in batch if row["id"] in existing_ids]
        to_delete = existing_ids - incoming_ids

        if to_insert:
            conn.execute(insert(tbl), to_insert)

        for row in to_update:
            stmt = (
                update(tbl)
                .where(tbl.c.id == row["id"])
                .values(**row)
            )
            conn.execute(stmt)

        if to_delete:
            conn.execute(
                delete(tbl).where(tbl.c.id.in_(to_delete))
            )

    print(
        f"🔄 Sync complete: +{len(to_insert)} inserted, "
        f"{len(to_update)} updated, -{len(to_delete)} deleted"
    )

    return len(to_insert), len(to_update), len(to_delete)
