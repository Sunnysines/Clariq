"""Google Search Service via SerpApi."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient


class OrganicResultItem(BaseModel):
    position: Optional[int] = None
    title: str
    link: Optional[str] = None
    displayed_link: Optional[str] = None
    snippet: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None


class SearchEngineResult(BaseModel):
    engine: str = "google_search"
    query: str
    location: Optional[str] = None
    total_results: Optional[int] = None
    results: list[OrganicResultItem] = Field(default_factory=list)
    raw_data: Optional[dict[str, Any]] = None


class GoogleSearchService:
    """Service for querying Google Web Search via SerpApi."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()

    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        num: int = 10,
    ) -> SearchEngineResult:
        params: dict[str, Any] = {
            "engine": "google",
            "q": query,
            "num": num,
        }
        if location:
            params["location"] = location

        raw = await self.client.execute(params)
        organic_items = raw.get("organic_results", [])
        
        parsed_results: list[OrganicResultItem] = []
        for idx, item in enumerate(organic_items):
            title = item.get("title", "")
            if not title:
                continue
            parsed_results.append(
                OrganicResultItem(
                    position=item.get("position", idx + 1),
                    title=title,
                    link=item.get("link"),
                    displayed_link=item.get("displayed_link"),
                    snippet=item.get("snippet"),
                    date=item.get("date"),
                    source=item.get("source") or item.get("displayed_link"),
                )
            )

        search_information = raw.get("search_information", {})
        total_results = search_information.get("total_results")

        return SearchEngineResult(
            engine="google_search",
            query=query,
            location=location,
            total_results=total_results,
            results=parsed_results,
            raw_data=raw,
        )
