from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Any


@dataclass
class EmbeddingRecord:
    id: str
    participants: List[str]
    combined_text: str
    calendar_name: str
    updated_at: datetime
    source: str
    message: List[float]
    status: str

    def to_dict(self) -> dict:
        return asdict(self)
