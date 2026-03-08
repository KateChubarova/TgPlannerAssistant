from typing import Dict

from langchain_core.tools import tool

from sources.web_search.client import simple_search


@tool
def location_info_tool(location: str) -> Dict:
    """
    Retrieve additional information about a location or meeting place.

    Use this tool when the user asks about the place where an event happens,
    for example:
    - where a meeting or interview takes place
    - details about a location from the calendar
    - information about a venue, address, office, or place name
    - how to get to a meeting location

    The tool performs a web search using the provided location string and
    returns a short structured summary that the assistant can use to answer
    the user's question.

    Args:
        location (str): The location string taken from a calendar event.
            This may be an address, office name, venue name, or place description.

    Returns:
        Dict: A dictionary containing:
            - location: the original location string
            - info: summarized search results about the location
    """

    result = simple_search(location, limit=3)

    return {
        "location": location,
        "info": f"Search results: {result}",
    }
