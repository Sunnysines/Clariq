"""Clariq ORM models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Analysis(Base):
    """Top-level analysis record."""

    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=_uuid)
    question = Column(Text, nullable=False)
    intent = Column(String, nullable=True)  # career / company / technology / compare
    mode = Column(String, nullable=True)  # intelligence mode
    status = Column(String, default="pending")  # pending | processing | completed | failed | partial
    current_stage = Column(String, nullable=True)
    overall_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    confidence_level = Column(String, nullable=True)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    searches = relationship("Search", back_populates="analysis", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="analysis", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="analysis", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="analysis", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="analysis", cascade="all, delete-orphan")


class Search(Base):
    """Record of a single SerpApi search execution."""

    __tablename__ = "searches"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    engine = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    result_count = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending | completed | failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    analysis = relationship("Analysis", back_populates="searches")
    evidence_items = relationship("Evidence", back_populates="search", cascade="all, delete-orphan")


class Evidence(Base):
    """Normalized evidence item from any SerpApi engine."""

    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    search_id = Column(String, ForeignKey("searches.id"), nullable=True)
    title = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # e.g. "linkedin.com", "naukri.com"
    source_type = Column(String, nullable=False)  # job | news | web | trend | local
    snippet = Column(Text, nullable=True)
    entity = Column(String, nullable=True)
    location = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    raw_engine = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    relevance_score = Column(Float, nullable=True)
    freshness_score = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)
    evidence_strength = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    analysis = relationship("Analysis", back_populates="evidence_items")
    search = relationship("Search", back_populates="evidence_items")


class Entity(Base):
    """Resolved entity aggregated from evidence."""

    __tablename__ = "entities"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # company | city | technology | job_role
    mention_count = Column(Integer, default=0)
    evidence_score = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    analysis = relationship("Analysis", back_populates="entities")


class Signal(Base):
    """Interpretable decision signal derived from evidence."""

    __tablename__ = "signals"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    entity = Column(String, nullable=True)
    type = Column(String, nullable=False)  # HIRING | DEMAND | GROWTH | INVESTMENT | POPULARITY | RECENCY | COMPETITION | RISK
    direction = Column(String, nullable=False)  # positive | negative | neutral
    strength = Column(Float, nullable=False)
    evidence_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    evidence_ids = Column(JSON, nullable=True)  # list of evidence IDs
    created_at = Column(DateTime, default=_utcnow)

    analysis = relationship("Analysis", back_populates="signals")


class Contradiction(Base):
    """Detected conflict between signals about the same entity."""

    __tablename__ = "contradictions"

    id = Column(String, primary_key=True, default=_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    entity_id = Column(String, nullable=True)
    entity_name = Column(String, nullable=True)
    positive_signal = Column(Text, nullable=True)
    negative_signal = Column(Text, nullable=True)
    severity = Column(String, nullable=True)  # low | medium | high
    confidence = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    evidence_ids = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    analysis = relationship("Analysis", back_populates="contradictions")
