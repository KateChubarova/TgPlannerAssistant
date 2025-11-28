import requests
from dataclasses import dataclass
from typing import List, Optional, Dict
import os

GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")
GOOGLE_SEARCH_URL = os.getenv("GOOGLE_SEARCH_URL")


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str
    address: Optional[str] = None
    telephone: Optional[str] = None
    rating: Optional[float] = None


def enrich_event_by_location(location: str) -> Dict:
    """
    Выполняет обогащение события по локации с помощью веб-поиска.
    """
    result = simple_search(location, limit=3)
    return {
        "raw_location": location,
        "info": f"Результат поиска по {result}",
    }


def format_location_info(results: list[WebResult]) -> str:
    """
    Форматирует результаты веб-поиска о локации в удобный текстовый вид.
    """
    if not results:
        return "Дополнительной информации о месте не нашлось."

    top = results[0]
    parts = [
        f"Ссылка: {top.url}",
        f"Описание: {top.snippet}",
    ]
    if top.address:
        parts.append(f"Адрес: {top.address}")
    if top.telephone:
        parts.append(f"Телефон: {top.telephone}")
    if top.rating:
        parts.append(f"Рейтинг: {top.rating}")

    return "\n".join(parts)


def simple_search(query: str, limit: int = 3) -> List[WebResult]:
    """
    Выполняет простой Google Custom Search по заданному запросу и возвращает
    список структурированных результатов.
    """
    resp = requests.get(
        GOOGLE_SEARCH_URL,
        params={
            "q": query,
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": GOOGLE_SEARCH_CX,
            "num": limit,
        },
        timeout=10,
    )
    data = resp.json()
    results: List[WebResult] = []

    for item in data.get("items", []):
        results.append(
            WebResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),

            )
        )

    print(results[0])
    return results[:limit]
