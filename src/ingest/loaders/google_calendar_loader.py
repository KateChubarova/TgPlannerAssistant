from typing import Iterable, Dict, Any, List
from ingest.providers.google_calendar import fetch_events
from sqlalchemy import insert

from shared.db import engine, tbl
from shared.models.calendar_event import CalendarEvent
from shared.models.mappers import map_event_to_embedding
from shared.nlp.embeddings import embed_calendar_event


def rows_from_events(events: Iterable[CalendarEvent]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ev in events:
        embedding_record = map_event_to_embedding(ev, embed_calendar_event(ev))
        rows.append(embedding_record.to_dict())
    return rows


def load_all_events() -> int:
    events = fetch_events(calendar_id="primary")
    batch = rows_from_events(events)
    if not batch:
        raise ValueError("Календарь пуст или не удалось извлечь события")

    with engine.begin() as conn:
        conn.execute(insert(tbl), batch)

    print(f"✅{len(batch)} events saved to public.tg_embeddings")
    return len(batch)
