import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

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
    Enrich event information using a location-based web search.

    This function performs a simple web search for the provided location and
    wraps the results into a structured dictionary that can be returned to
    the language model as a tool output.

    Args:
        location (str): The location string to search for additional information.

    Return:
        Dict: A dictionary containing the raw location and a formatted search result.
    """
    result = simple_search(location, limit=3)
    return {
        "raw_location": location,
        "info": f"Результат поиска по {result}",
    }


def format_location_info(results: list[WebResult]) -> str:
    """
    Format detailed information about a location into a readable text block.

    This function takes a list of web search results, selects the most relevant
    one, and constructs a human-readable description including URL, snippet,
    address, phone, and rating if available.

    Args:
        results (list[WebResult]): A list of web search result objects.

    Return:
        str: A formatted description of the top search result, or a fallback message
            if no results are available.
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
    Perform a simple Google Custom Search query and return structured results.

    This function sends a request to the Google Custom Search API, parses the
    response, and converts search results into WebResult dataclass instances.

    Args:
        query (str): The text query to search for.
        limit (int): The maximum number of results to return (default is 3).

    Return:
        List[WebResult]: A list of structured web results limited to the specified amount.
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
