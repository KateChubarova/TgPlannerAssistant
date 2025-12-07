import os
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from sqlalchemy import select, delete

from shared.mapper import map_events
from shared.models.embedding import Embedding
from sources.google_calendar.google_auth import get_creds
from shared.storage.db import SessionLocal
from shared.models.calendar_event import CalendarEvent
from shared.models.user import TgUser

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS")


def load_all_events(user: TgUser) -> {int}:
    """
    Load all calendar events for a user and synchronize them with the database.

    This function fetches events from the user's Google Calendar, maps them into
    embedding objects, and then inserts, updates, or deletes records in the
    database to reflect the current state of the calendar.

    Args:
        user (TgUser): The Telegram user whose Google Calendar events should be synchronized.

    Return:
        tuple[int, int, int]: A tuple containing the number of inserted, updated,
            and deleted records in that order.
    """
    events = fetch_events(user)
    batch = map_events(user, events)
    if not batch:
        raise ValueError("Календарь пуст или не удалось извлечь события")

    incoming_ids = {event.id for event in batch}

    with SessionLocal() as session:
        existing_ids = set(
            session.scalars(
                select(Embedding.id)
                .where(Embedding.user_id == user.id)
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
                delete(Embedding)
                .where(Embedding.id.in_(to_delete))
            )
        session.commit()

    return len(to_insert), len(to_update), len(to_delete)


def fetch_events(user: TgUser, calendar_id: str = "primary", time_min: datetime = None,
                 time_max: datetime = None, max_results: int = 2500) -> [CalendarEvent]:
    """
    Fetch events from a user's Google Calendar within a given time range.

    This function calls the Google Calendar API using the user's credentials and
    yields CalendarEvent objects for each event found in the specified calendar
    and time window.

    Args:
        user (TgUser): The Telegram user whose Google Calendar should be queried.
        calendar_id (str): The ID of the calendar to fetch events from, default is "primary".
        time_min (datetime): The start of the time range to query. If None, uses the current UTC time.
        time_max (datetime): The end of the time range to query. If None, uses 180 days from now.
        max_results (int): The maximum number of events to return from the API.

    Return:
        list[CalendarEvent]: A list of CalendarEvent objects representing the events
            retrieved from the Google Calendar API.
    """
    creds = get_creds(user)
    service = build("calendar", "v3", credentials=creds)

    if time_min is None:
        time_min = datetime.utcnow() - timedelta(days=0)
    if time_max is None:
        time_max = datetime.utcnow() + timedelta(days=180)

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min.isoformat() + "Z",
        timeMax=time_max.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    for item in events_result.get("items", []):
        yield CalendarEvent(
            id=item.get("id"),
            source="google",
            calendar=calendar_id,
            title=item.get("summary"),
            description=item.get("description"),
            location=item.get("location"),
            participants=[a.get("email") or a.get("displayName") or "" for a in item.get("attendees", [])],
            start_ts=item.get("start"),
            end_ts=item.get("end"),
            status="confirmed"
        )
