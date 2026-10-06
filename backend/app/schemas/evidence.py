"""Evidence Schemas – Unified representation for normalized SerpApi records."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


SourceType = Literal["job", "news", "web", "trend", "local"]


class NormalizedEvidence(BaseModel):
    """Normalized evidence representation produced by EvidenceEngine."""

    id: Optional[str] = None
    analysis_id: str
    search_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    source_type: SourceType
    snippet: Optional[str] = None
    entity: Optional[str] = None
    location: Optional[str] = None
    published_at: Optional[datetime] = None
    raw_engine: Optional[str] = None
    raw_data: Optional[dict[str, Any]] = None

    # Evaluation scores (0 - 100)
    relevance_score: Optional[float] = None
    freshness_score: Optional[float] = None
    reliability_score: Optional[float] = None
    evidence_strength: Optional[float] = None
    created_at: Optional[datetime] = None


class EvidenceSummary(BaseModel):
    """High-level summary of evidence count per source type."""

    total_count: int
    by_source_type: dict[str, int] = Field(default_factory=dict)
    average_strength: Optional[float] = None
