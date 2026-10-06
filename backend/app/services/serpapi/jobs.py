"""Google Jobs Service via SerpApi."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient


class JobResultItem(BaseModel):
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    via: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    posted_at: Optional[str] = None
    extensions: list[str] = Field(default_factory=list)
    schedule_type: Optional[str] = None


class JobsEngineResult(BaseModel):
    engine: str = "google_jobs"
    query: str
    location: Optional[str] = None
    results: list[JobResultItem] = Field(default_factory=list)
    raw_data: Optional[dict[str, Any]] = None


class GoogleJobsService:
    """Service for querying Google Jobs via SerpApi."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()

    async def search(
        self,
        query: str,
        location: Optional[str] = None,
    ) -> JobsEngineResult:
        params: dict[str, Any] = {
            "engine": "google_jobs",
            "q": query,
        }
        if location:
            params["location"] = location

        raw = await self.client.execute(params)
        raw_jobs = raw.get("jobs_results", [])

        parsed_jobs: list[JobResultItem] = []
        for item in raw_jobs:
            title = item.get("title", "")
            if not title:
                continue

            # Check related links / apply options for URL
            apply_options = item.get("apply_options", [])
            primary_link = None
            if apply_options and isinstance(apply_options, list):
                primary_link = apply_options[0].get("link")
            if not primary_link:
                primary_link = item.get("share_link")

            parsed_jobs.append(
                JobResultItem(
                    title=title,
                    company_name=item.get("company_name"),
                    location=item.get("location"),
                    via=item.get("via"),
                    description=item.get("description"),
                    link=primary_link,
                    posted_at=item.get("detected_extensions", {}).get("posted_at"),
                    extensions=item.get("extensions", []),
                    schedule_type=item.get("detected_extensions", {}).get("schedule_type"),
                )
            )

        return JobsEngineResult(
            engine="google_jobs",
            query=query,
            location=location,
            results=parsed_jobs,
            raw_data=raw,
        )
