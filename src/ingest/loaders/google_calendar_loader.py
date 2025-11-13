from typing import Iterable, Dict, Any, List
import os
from ingest.providers.google_calendar import fetch_events
from sqlalchemy import create_engine, MetaData, Table, insert
from openai import OpenAI
from shared.models.calendar_event import CalendarEvent
from shared.models.mappers import map_event_to_embedding

ENGINE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://k.chubarava@localhost/postgres")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

engine = create_engine(ENGINE_URL, future=True)
client = OpenAI(api_key=OPENAI_API_KEY)

meta = MetaData()
tbl = Table("tg_embeddings", meta, autoload_with=engine, schema="public")


def embed(event: CalendarEvent):
    resp = client.embeddings.create(model=MODEL, input=event.to_str())
    return resp.data[0].embedding


def rows_from_events(events: Iterable[CalendarEvent]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ev in events:
        embedding_record = map_event_to_embedding(ev, embed(ev))
        rows.append(embedding_record.to_dict())
    return rows


def load_all_events():
    events = fetch_events(calendar_id="primary")
    batch = rows_from_events(events)
    if not batch:
        print("nothing fetched from calendar")
        return

    with engine.begin() as conn:
        conn.execute(insert(tbl), batch)

    print(f"✅{len(batch)} events saved to public.tg_embeddings")


load_all_events()
