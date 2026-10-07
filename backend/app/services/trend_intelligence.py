"""Trend Intelligence Engine – interprets Google Trends data as SEARCH INTEREST signals.

Key design rules (per Clariq product spec):
- Trends data is labelled "SEARCH INTEREST", not hiring demand or job availability.
- A high trend index does NOT directly imply jobs are available.
- Trends are one evidence channel among multiple; they feed into POPULARITY and DEMAND signals.
- Each trend result carries:
    • search_term
    • average_interest (0-100)
    • timeline (date, value)
    • geo / time_range
    • interest_label = "SEARCH INTEREST"   (always explicit)
    • comparison_entities (if comparative query was used)
- Trends are cached to avoid redundant API calls.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.services.serpapi.trends import GoogleTrendsService, TrendsEngineResult, TrendResultItem

logger = logging.getLogger("clariq.trend_intelligence")


# ---------- Output Models ----------

class TrendTimelinePoint(BaseModel):
    date: str
    value: int  # 0-100 relative search interest


class EntityTrendProfile(BaseModel):
    """Search interest profile for a single query / entity."""
    search_term: str
    interest_label: str = "SEARCH INTEREST"  # always explicit – never implied to mean jobs
    geo: Optional[str] = None
    time_range: str = "Past 12 months"
    average_interest: Optional[float] = None       # 0-100 relative scale
    peak_interest: Optional[int] = None
    trend_direction: str = "stable"                # rising | falling | stable | insufficient_data
    timeline: list[TrendTimelinePoint] = Field(default_factory=list)
    evidence_id: Optional[str] = None
    warning: Optional[str] = None


class ComparativeTrendResult(BaseModel):
    """Side-by-side interest comparison for multiple entities (e.g., cities or technologies)."""
    entities: list[str]
    geo: Optional[str] = None
    time_range: str = "Past 12 months"
    profiles: list[EntityTrendProfile] = Field(default_factory=list)
    interest_label: str = "SEARCH INTEREST"
    interpretation_note: str = (
        "Search interest measures relative public attention, not job availability or hiring demand. "
        "It is one signal among multiple evidence channels."
    )


class TrendIntelligenceResult(BaseModel):
    """Processed trend intelligence output for an analysis."""
    analysis_id: str
    query_topic: str
    profiles: list[EntityTrendProfile] = Field(default_factory=list)
    comparative: Optional[ComparativeTrendResult] = None
    signal_type: str = "POPULARITY"          # maps to signal engine POPULARITY
    evidence_ids: list[str] = Field(default_factory=list)
    warning: Optional[str] = None


# ---------- Engine ----------

class TrendIntelligenceEngine:
    """Converts raw Google Trends SerpApi results into labelled SEARCH INTEREST signals."""

    def __init__(self, trends_service: Optional[GoogleTrendsService] = None):
        self._trends = trends_service or GoogleTrendsService()

    @staticmethod
    def _classify_direction(timeline: list[TrendTimelinePoint]) -> str:
        """Classify trend direction from timeline."""
        if len(timeline) < 4:
            return "insufficient_data"
        values = [p.value for p in timeline if p.value > 0]
        if not values:
            return "insufficient_data"
        # Compare last quarter to first quarter
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(values[mid:]) / (len(values) - mid) if (len(values) - mid) > 0 else 0
        if second_half_avg > first_half_avg * 1.15:
            return "rising"
        elif second_half_avg < first_half_avg * 0.85:
            return "falling"
        return "stable"

    @staticmethod
    def _build_profile_from_result(
        result: TrendResultItem,
        geo: Optional[str],
        analysis_id: str,
    ) -> EntityTrendProfile:
        timeline = [
            TrendTimelinePoint(date=pt.date, value=pt.value or 0)
            for pt in result.timeline_data
        ]
        eid = str(uuid.uuid4())
        direction = TrendIntelligenceEngine._classify_direction(timeline)
        peak = max((p.value for p in timeline), default=None)

        return EntityTrendProfile(
            search_term=result.query,
            geo=geo or "Global",
            average_interest=result.average_interest,
            peak_interest=peak,
            trend_direction=direction,
            timeline=timeline,
            evidence_id=eid,
        )

    async def get_trend_profile(
        self,
        topic: str,
        analysis_id: str,
        geo: Optional[str] = "IN",
    ) -> TrendIntelligenceResult:
        """Get trend intelligence for a single topic."""
        logger.info(f"TrendIntelligence: fetching single profile for '{topic}' geo={geo}")
        try:
            raw: TrendsEngineResult = await self._trends.search(query=topic, geo=geo)
            profiles = [
                self._build_profile_from_result(r, geo, analysis_id)
                for r in raw.results
            ]
            ev_ids = [p.evidence_id for p in profiles if p.evidence_id]
            return TrendIntelligenceResult(
                analysis_id=analysis_id,
                query_topic=topic,
                profiles=profiles,
                evidence_ids=ev_ids,
            )
        except Exception as exc:
            logger.warning(f"TrendIntelligence failed for '{topic}': {exc}")
            return TrendIntelligenceResult(
                analysis_id=analysis_id,
                query_topic=topic,
                profiles=[],
                warning=f"Trend data unavailable: {type(exc).__name__}",
            )

    async def get_comparative_trends(
        self,
        entities: list[str],
        analysis_id: str,
        geo: Optional[str] = "IN",
    ) -> TrendIntelligenceResult:
        """Get comparative search interest across multiple entities.

        Uses a single comma-joined query where SerpApi supports it, or
        individual queries where not – to avoid unnecessary API calls.
        """
        logger.info(f"TrendIntelligence: comparative for {entities} geo={geo}")
        profiles: list[EntityTrendProfile] = []
        ev_ids: list[str] = []

        # Use individual queries (SerpApi trends works best per-entity for accuracy)
        for entity in entities[:4]:  # Cap at 4 to avoid excessive calls
            try:
                raw = await self._trends.search(query=entity, geo=geo)
                for r in raw.results:
                    p = self._build_profile_from_result(r, geo, analysis_id)
                    profiles.append(p)
                    if p.evidence_id:
                        ev_ids.append(p.evidence_id)
            except Exception as exc:
                logger.warning(f"TrendIntelligence: comparative entity '{entity}' failed: {exc}")
                profiles.append(EntityTrendProfile(
                    search_term=entity,
                    geo=geo or "IN",
                    trend_direction="insufficient_data",
                    warning=f"Unavailable: {type(exc).__name__}",
                ))

        comparative = ComparativeTrendResult(
            entities=entities,
            geo=geo,
            profiles=profiles,
        )

        return TrendIntelligenceResult(
            analysis_id=analysis_id,
            query_topic=" vs ".join(entities),
            profiles=profiles,
            comparative=comparative,
            evidence_ids=ev_ids,
        )
