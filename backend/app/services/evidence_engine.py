"""EvidenceEngine – normalizes heterogeneous SerpApi engine outputs into unified evidence models."""
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from app.schemas.evidence import NormalizedEvidence, SourceType
from app.services.serpapi.search import SearchEngineResult, OrganicResultItem
from app.services.serpapi.jobs import JobsEngineResult, JobResultItem
from app.services.serpapi.news import NewsEngineResult, NewsResultItem
from app.services.serpapi.trends import TrendsEngineResult, TrendResultItem
from app.services.serpapi.local import LocalEngineResult, LocalResultItem
from app.services.serpapi.orchestrator import EngineExecutionReport

logger = logging.getLogger("clariq.evidence_engine")


def _parse_relative_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse common SerpApi date formats into UTC datetime, without fabricating missing dates."""
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned = date_str.strip().lower()
    now = datetime.now(timezone.utc)

    # Relative expressions
    if "just now" in cleaned or "moments ago" in cleaned:
        return now

    match_hours = re.search(r"(\d+)\s*(?:hour|hr|hours)s?\s*ago", cleaned)
    if match_hours:
        return now - timedelta(hours=int(match_hours.group(1)))

    match_days = re.search(r"(\d+)\s*(?:day|days)\s*ago", cleaned)
    if match_days:
        return now - timedelta(days=int(match_days.group(1)))

    match_weeks = re.search(r"(\d+)\s*(?:week|weeks|wk)s?\s*ago", cleaned)
    if match_weeks:
        return now - timedelta(weeks=int(match_weeks.group(1)))

    match_months = re.search(r"(\d+)\s*(?:month|months|mo)s?\s*ago", cleaned)
    if match_months:
        return now - timedelta(days=int(match_months.group(1)) * 30)

    # Standard date parsers
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%d %b %Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    return None


class EvidenceEngine:
    """Normalizes raw results across Google Search, Jobs, News, Trends, and Local."""

    @staticmethod
    def normalize_search_item(
        item: OrganicResultItem,
        analysis_id: str,
        search_id: Optional[str] = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> NormalizedEvidence:
        """Normalize a Google Search result."""
        published_dt = _parse_relative_date(item.date)

        # Extract domain/source if not explicitly set
        source = item.source or (item.displayed_link.split("/")[0] if item.displayed_link else None)

        return NormalizedEvidence(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            search_id=search_id,
            title=item.title,
            url=item.link,
            source=source,
            source_type="web",
            snippet=item.snippet,
            entity=None,  # to be resolved by EntityResolver
            location=location,
            published_at=published_dt,
            raw_engine="google_search",
            raw_data=item.model_dump(),
        )

    @staticmethod
    def normalize_job_item(
        item: JobResultItem,
        analysis_id: str,
        search_id: Optional[str] = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> NormalizedEvidence:
        """Normalize a Google Jobs result."""
        published_dt = _parse_relative_date(item.posted_at)
        source = item.via.replace("via ", "").strip() if item.via else "Google Jobs"

        # Combine title, company, description and extensions into rich snippet
        ext_text = f" [{', '.join(item.extensions)}]" if item.extensions else ""
        snippet_parts = [
            f"Role at {item.company_name}" if item.company_name else "Open Job Position",
            item.description or "",
            ext_text,
        ]
        snippet = " - ".join(p for p in snippet_parts if p).strip()

        return NormalizedEvidence(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            search_id=search_id,
            title=f"{item.title} ({item.company_name})" if item.company_name else item.title,
            url=item.link,
            source=source,
            source_type="job",
            snippet=snippet or None,
            entity=item.company_name,  # Raw entity hypothesis
            location=item.location or location,
            published_at=published_dt,
            raw_engine="google_jobs",
            raw_data=item.model_dump(),
        )

    @staticmethod
    def normalize_news_item(
        item: NewsResultItem,
        analysis_id: str,
        search_id: Optional[str] = None,
        query: Optional[str] = None,
        location: Optional[str] = None,
    ) -> NormalizedEvidence:
        """Normalize a Google News result."""
        published_dt = _parse_relative_date(item.date)

        return NormalizedEvidence(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            search_id=search_id,
            title=item.title,
            url=item.link,
            source=item.source or "Google News",
            source_type="news",
            snippet=item.snippet,
            entity=None,
            location=location,
            published_at=published_dt,
            raw_engine="google_news",
            raw_data=item.model_dump(),
        )

    @staticmethod
    def normalize_trends_item(
        item: TrendResultItem,
        analysis_id: str,
        search_id: Optional[str] = None,
        geo: Optional[str] = None,
    ) -> NormalizedEvidence:
        """Normalize a Google Trends result."""
        avg_val = item.average_interest or 0
        points_count = len(item.timeline_data)
        snippet = (
            f"Google Trends query '{item.query}' measured an average relative search volume "
            f"index of {avg_val}/100 across {points_count} chronological observations."
        )

        return NormalizedEvidence(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            search_id=search_id,
            title=f"Google Trends Search Demand Index: {item.query}",
            url=None,  # Trends has no direct single page URL
            source="Google Trends",
            source_type="trend",
            snippet=snippet,
            entity=item.query,
            location=geo,
            published_at=datetime.now(timezone.utc),  # Trends represents current aggregate
            raw_engine="google_trends",
            raw_data=item.model_dump(),
        )

    @staticmethod
    def normalize_local_item(
        item: LocalResultItem,
        analysis_id: str,
        search_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> NormalizedEvidence:
        """Normalize a Google Local Maps place result."""
        snippet_parts = []
        if item.type:
            snippet_parts.append(f"Category: {item.type}")
        if item.address:
            snippet_parts.append(f"Address: {item.address}")
        if item.rating:
            snippet_parts.append(f"Rating: {item.rating}★ ({item.reviews or 0} reviews)")
        
        snippet = " | ".join(snippet_parts)

        return NormalizedEvidence(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            search_id=search_id,
            title=item.title,
            url=item.website,
            source="Google Maps / Local",
            source_type="local",
            snippet=snippet or None,
            entity=item.title,
            location=item.address or location,
            published_at=None,
            raw_engine="google_local",
            raw_data=item.model_dump(),
        )

    def normalize_report(
        self,
        report: EngineExecutionReport,
        analysis_id: str,
        search_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> list[NormalizedEvidence]:
        """Convert an engine execution report into a list of normalized evidence items."""
        if report.status != "completed" or not report.output:
            return []

        out = report.output
        items: list[NormalizedEvidence] = []

        if isinstance(out, SearchEngineResult):
            for res in out.results:
                items.append(self.normalize_search_item(res, analysis_id, search_id, out.query, out.location or location))

        elif isinstance(out, JobsEngineResult):
            for res in out.results:
                items.append(self.normalize_job_item(res, analysis_id, search_id, out.query, out.location or location))

        elif isinstance(out, NewsEngineResult):
            for res in out.results:
                items.append(self.normalize_news_item(res, analysis_id, search_id, out.query, out.location or location))

        elif isinstance(out, TrendsEngineResult):
            for res in out.results:
                items.append(self.normalize_trends_item(res, analysis_id, search_id, out.geo or location))

        elif isinstance(out, LocalEngineResult):
            for res in out.results:
                items.append(self.normalize_local_item(res, analysis_id, search_id, out.location or location))

        return items
