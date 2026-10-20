
import httpx

from backend.config import settings


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def search_web(query: str, max_results: int = 5) -> list[dict]:
    if not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is missing from .env")

    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TAVILY_SEARCH_URL,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return [
        {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0.0),
        }
        for result in data.get("results", [])
    ]


def get_web_search_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the public web for current information or facts "
                "that are missing from the provided video transcript."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    }
