"""Pydantic schemas for API request/response boundaries."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------- Health ----------
class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "clariq-backend"
    version: str = "0.1.0"


# ---------- Analysis Request / Response ----------
class AnalyzeRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)


class AnalyzeStartResponse(BaseModel):
    analysis_id: str
    status: str


class AnalysisStatus(BaseModel):
    id: str
    question: str
    intent: Optional[str] = None
    mode: Optional[str] = None
    status: str
    current_stage: Optional[str] = None
    overall_score: Optional[float] = None
    confidence_score: Optional[float] = None
    confidence_level: Optional[str] = None
    result_data: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisListItem(BaseModel):
    id: str
    question: str
    intent: Optional[str] = None
    mode: Optional[str] = None
    status: str
    overall_score: Optional[float] = None
    confidence_level: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisListResponse(BaseModel):
    total: int
    items: list[AnalysisListItem]


# ---------- Evidence ----------
class EvidenceItem(BaseModel):
    id: str
    analysis_id: str
    search_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    source_type: str
    snippet: Optional[str] = None
    entity: Optional[str] = None
    location: Optional[str] = None
    published_at: Optional[datetime] = None
    relevance_score: Optional[float] = None
    freshness_score: Optional[float] = None
    reliability_score: Optional[float] = None
    evidence_strength: Optional[float] = None


class EvidenceListResponse(BaseModel):
    analysis_id: str
    total: int
    items: list[EvidenceItem]


# ---------- Entity ----------
class EntityItem(BaseModel):
    id: str
    analysis_id: str
    name: str
    normalized_name: str
    type: str
    mention_count: int
    evidence_score: Optional[float] = None


class EntityListResponse(BaseModel):
    analysis_id: str
    total: int
    items: list[EntityItem]


# ---------- Signal ----------
class SignalItem(BaseModel):
    id: str
    analysis_id: str
    entity: Optional[str] = None
    type: str
    direction: str
    strength: float
    evidence_count: int
    description: Optional[str] = None
    evidence_ids: Optional[list[str]] = None


class SignalListResponse(BaseModel):
    analysis_id: str
    total: int
    items: list[SignalItem]


# ---------- Contradiction ----------
class ContradictionItem(BaseModel):
    id: str
    analysis_id: str
    entity_name: Optional[str] = None
    positive_signal: Optional[str] = None
    negative_signal: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
    description: Optional[str] = None
    evidence_ids: Optional[list[str]] = None


# ---------- Compare ----------
class CompareRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    entities: Optional[list[str]] = None
    mode: Optional[str] = "career"
