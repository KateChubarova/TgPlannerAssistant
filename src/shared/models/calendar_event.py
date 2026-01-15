from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Organizer:
    id: str
    email: str
    displayName: str
    self: bool


@dataclass
class CalendarEvent:
    event_id: str
    title: str
    calendar: str
    description: Optional[str]
    location: Optional[str]
    participants: List[str]
    start_ts: dict
    end_ts: dict
    updated: datetime
    organizer: Organizer

    def to_str(self) -> str:
        parts: List[str] = []
        if self.title:
            parts.append(self.title)
        if self.description:
            parts.append(self.description)
        if self.location:
            parts.append(f"Location: {self.location}")
        if self.participants:
            parts.append("Participants: " + ", ".join(self.participants))
        if self.start_ts and self.end_ts:
            parts.append(f"Time: {self.start_ts} – {self.end_ts}")
        if self.organizer:
            parts.append(
                f"Organizer: {self.organizer.displayName} ({self.organizer.email})"
            )
        return " | ".join(parts)
