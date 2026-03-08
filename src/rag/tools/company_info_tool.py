from langchain_core.tools import tool

from sources.web_search.client import simple_search


@tool
def company_info_tool(company_name: str) -> dict:
    """
    Fetch public information about a company using web search.

    Use this tool when the company name has already been inferred
    from event data (title, organizer_email, organizer_display_name).

    The tool performs a web search and returns raw results that help
    the model answer questions like:
    "What do you know about our company?"

    Args:
        company_name: Name of the company.

    Returns:
        Dictionary containing the company name and search results.
    """

    results = simple_search(company_name, limit=3)

    return {
        "company_name": company_name,
        "web_results": results,
    }
