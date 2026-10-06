"""Google Trends Service via SerpApi."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient


class TrendDataPoint(BaseModel):
    date: str
    value: int
    extracted_value: Optional[int] = None


class TrendResultItem(BaseModel):
    query: str
    average_interest: Optional[float] = None
    timeline_data: list[TrendDataPoint] = Field(default_factory=list)


class TrendsEngineResult(BaseModel):
    engine: str = "google_trends"
    query: str
    geo: Optional[str] = None
    results: list[TrendResultItem] = Field(default_factory=list)
    raw_data: Optional[dict[str, Any]] = None


class GoogleTrendsService:
    """Service for querying Google Trends via SerpApi."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()

    async def search(
        self,
        query: str,
        geo: Optional[str] = None,
        data_type: str = "TIMESERIES",
    ) -> TrendsEngineResult:
        params: dict[str, Any] = {
            "engine": "google_trends",
            "q": query,
            "data_type": data_type,
        }
        if geo:
            params["geo"] = geo

        raw = await self.client.execute(params)
        interest_over_time = raw.get("interest_over_time", {})
        timeline_list = interest_over_time.get("timeline_data", [])

        parsed_points: list[TrendDataPoint] = []
        total_val = 0
        count = 0
        for pt in timeline_list:
            date_str = pt.get("date", "")
            values = pt.get("values", [])
            val = 0
            if values and isinstance(values, list) and len(values) > 0:
                first_val = values[0]
                val = int(first_val.get("extracted_value", 0)) if isinstance(first_val, dict) else int(first_val or 0)
            
            parsed_points.append(
                TrendDataPoint(
                    date=date_str,
                    value=val,
                    extracted_value=val,
                )
            )
            total_val += val
            count += 1

        avg = round(total_val / count, 1) if count > 0 else None

        trend_item = TrendResultItem(
            query=query,
            average_interest=avg,
            timeline_data=parsed_points,
        )

        return TrendsEngineResult(
            engine="google_trends",
            query=query,
            geo=geo,
            results=[trend_item],
            raw_data=raw,
        )
