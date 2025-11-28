import os
from datetime import datetime, timedelta

from googleapiclient.discovery import build

from ingest.providers.google_auth import get_creds
from shared.models.calendar_event import CalendarEvent
from shared.models.user import TgUser

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN")


def fetch_events(user: TgUser, calendar_id: str = "primary", time_min: datetime | None = None,
                 time_max: datetime | None = None,
                 max_results: int = 2500) -> [CalendarEvent]:
    """
    Получает события Google Calendar для указанного пользователя и возвращает их в виде генератора CalendarEvent.
    По умолчанию загружает все будущие события в диапазоне от текущего момента
    до 180 дней вперёд, но диапазон можно переопределить.
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
