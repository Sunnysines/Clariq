"""Google News Service via SerpApi."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient


class NewsResultItem(BaseModel):
    position: Optional[int] = None
    title: str
    link: Optional[str] = None
    source: Optional[str] = None
    date: Optional[str] = None
    snippet: Optional[str] = None
    thumbnail: Optional[str] = None


class NewsEngineResult(BaseModel):
    engine: str = "google_news"
    query: str
    location: Optional[str] = None
    results: list[NewsResultItem] = Field(default_factory=list)
    raw_data: Optional[dict[str, Any]] = None


class GoogleNewsService:
    """Service for querying Google News via SerpApi."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()

    async def search(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> NewsEngineResult:
        params: dict[str, Any] = {
            "engine": "google_news",
            "q": query,
        }
        if location:
            params["location"] = location

        raw = await self.client.execute(params)
        raw_news = raw.get("news_results", [])

        parsed_news: list[NewsResultItem] = []
        for idx, item in enumerate(raw_news):
            title = item.get("title", "")
            if not title:
                continue

            source_info = item.get("source")
            source_name = source_info.get("name") if isinstance(source_info, dict) else str(source_info or "")

            parsed_news.append(
                NewsResultItem(
                    position=item.get("position", idx + 1),
                    title=title,
                    link=item.get("link"),
                    source=source_name or None,
                    date=item.get("date"),
                    snippet=item.get("snippet"),
                    thumbnail=item.get("thumbnail"),
                )
            )

        return NewsEngineResult(
            engine="google_news",
            query=query,
            location=location,
            results=parsed_news,
            raw_data=raw,
        )
