"""Google Local / Maps Service via SerpApi."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient


class LocalResultItem(BaseModel):
    position: Optional[int] = None
    title: str
    address: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    type: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    links: Optional[dict[str, str]] = None


class LocalEngineResult(BaseModel):
    engine: str = "google_local"
    query: str
    location: Optional[str] = None
    results: list[LocalResultItem] = Field(default_factory=list)
    raw_data: Optional[dict[str, Any]] = None


class GoogleLocalService:
    """Service for querying Google Maps / Local Places via SerpApi."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()

    async def search(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> LocalEngineResult:
        params: dict[str, Any] = {
            "engine": "google_maps",
            "q": query,
            "type": "search",
        }
        # NOTE: SerpApi google_maps requires `z`/`m` whenever `location` is sent.
        # City context is carried in the query text instead (e.g. "tech parks in Pune").
        _ = location

        raw = await self.client.execute(params)
        raw_local = raw.get("local_results", [])

        parsed_items: list[LocalResultItem] = []
        for idx, item in enumerate(raw_local):
            title = item.get("title", "")
            if not title:
                continue

            website_url = item.get("website") or (item.get("links", {}) or {}).get("website")

            parsed_items.append(
                LocalResultItem(
                    position=item.get("position", idx + 1),
                    title=title,
                    address=item.get("address"),
                    rating=item.get("rating"),
                    reviews=item.get("reviews"),
                    type=item.get("type"),
                    phone=item.get("phone"),
                    website=website_url,
                    links=item.get("links") if isinstance(item.get("links"), dict) else None,
                )
            )

        return LocalEngineResult(
            engine="google_local",
            query=query,
            location=location,
            results=parsed_items,
            raw_data=raw,
        )
