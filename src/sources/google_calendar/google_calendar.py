import os
from datetime import datetime, timedelta

from dateutil import parser
from googleapiclient.discovery import build
from sqlalchemy import delete, select

from shared.mapper import map_events
from shared.models.calendar_event import CalendarEvent, Organizer
from shared.models.embedding import Embedding
from shared.models.user import TgUser
from shared.storage.db import SessionLocal
from sources.google_calendar.google_auth import get_creds

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS")


def load_all_events(user: TgUser, progress_callback: callable) -> tuple[int, int, int]:
    """
    Load all calendar events for a user and synchronize them with the database.

    This function fetches events from the user's Google Calendar, maps them into
    embedding objects, and then inserts, updates, or deletes records in the
    database to reflect the current state of the calendar.

    Args:
        user (TgUser): The Telegram user whose Google Calendar events should be synchronized.
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
        tuple[int, int, int]: A tuple containing the number of inserted, updated,
            and deleted records in that order.
    """
    events = fetch_events(user)

    if not events:
        raise ValueError("Календарь пуст или не удалось извлечь события")

    incoming_ids = {e.event_id for e in events}

    with SessionLocal() as session:
        existing_rows = session.scalars(
            select(Embedding).where(Embedding.user_id == user.id)
        ).all()

        existing_by_id = {row.event_id: row for row in existing_rows}
        existing_ids = set(existing_by_id.keys())

        ids_to_insert = incoming_ids - existing_ids
        ids_to_update: set[str] = set()

        for event in events:
            row = existing_by_id.get(event.event_id)
            if not row:
                continue

            if row.updated is None or event.updated is None:
                ids_to_update.add(event.event_id)
            elif event.updated > row.updated:
                ids_to_update.add(event.event_id)

        ids_to_delete = existing_ids - incoming_ids

        ids_need_mapping = ids_to_insert | ids_to_update
        events_to_map = [e for e in events if e.event_id in ids_need_mapping]

        batch = map_events(user, events_to_map, progress_callback=progress_callback)

        to_insert = [row for row in batch if row.event_id in ids_to_insert]
        to_update = [row for row in batch if row.event_id in ids_to_update]

        if to_insert:
            session.add_all(to_insert)

        if to_update:
            for row in to_update:
                session.merge(row)

        if ids_to_delete:
            session.execute(
                delete(Embedding).where(
                    Embedding.user_id == user.id,
                    Embedding.event_id.in_(ids_to_delete),
                )
            )

        session.commit()

    return len(to_insert), len(to_update), len(ids_to_delete)


def fetch_events(
    user: TgUser,
    calendar_id: str = "primary",
    time_min: datetime = None,
    time_max: datetime = None,
    max_results: int = 2500,
) -> [CalendarEvent]:
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

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat() + "Z",
            timeMax=time_max.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
            maxResults=max_results,
        )
        .execute()
    )

    return [
        CalendarEvent(
            event_id=item.get("id"),
            calendar=calendar_id,
            title=item.get("summary"),
            description=item.get("description"),
            location=item.get("location"),
            participants=[
                a.get("email") or a.get("displayName") or ""
                for a in item.get("attendees", [])
            ],
            start_ts=item.get("start"),
            end_ts=item.get("end"),
            updated=parser.isoparse(item.get("updated")),
            organizer=Organizer(
                id=item.get("organizer", {}).get("id"),
                email=item.get("organizer", {}).get("email"),
                displayName=item.get("organizer", {}).get("displayName"),
                self=item.get("organizer", {}).get("self"),
            ),
        )
        for item in events_result.get("items", [])
    ]
