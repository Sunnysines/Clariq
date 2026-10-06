"""Relevance & Reliability Evaluation Engine for Clariq Evidence.

Calculates:
- relevance_score (0-100) via keyword overlap, semantic density, intent match, and location match
- reliability_score (0-100) via source categorization heuristics
- freshness_score (0-100) via FreshnessEngine
- evidence_strength (0-100) = 0.5 * relevance + 0.3 * freshness + 0.2 * reliability
"""
from __future__ import annotations

import re
from typing import Optional

from app.schemas.evidence import NormalizedEvidence
from app.services.freshness_engine import FreshnessEngine


class ReliabilityScorer:
    """Configurable source reliability assumptions (Clariq Product Assumptions).

    These assumptions reflect Clariq's baseline heuristic weighting of primary channels
    and domain authorities, rather than absolute objective truth.
    """

    RELIABILITY_TABLE = {
        "official_company": 95.0,
        "google_jobs": 90.0,
        "major_news": 90.0,
        "company_blog": 85.0,
        "general_web": 70.0,
        "forum": 50.0,
        "default": 65.0,
    }

    MAJOR_NEWS_DOMAINS = {
        "reuters.com", "bloomberg.com", "techcrunch.com", "economictimes.indiatimes.com",
        "livemint.com", "thehindu.com", "timesofindia.indiatimes.com", "business-standard.com",
        "forbes.com", "wsj.com", "cnbc.com", "venturebeat.com", "moneycontrol.com"
    }

    FORUM_DOMAINS = {
        "reddit.com", "quora.com", "medium.com", "x.com", "twitter.com", "blind.com"
    }

    @classmethod
    def calculate_reliability(cls, source: Optional[str], source_type: str, url: Optional[str]) -> float:
        """Evaluate source credibility based on domain pattern and source type."""
        low_src = (source or "").lower()
        low_url = (url or "").lower()

        # Job platforms have direct structured listing verification
        if source_type == "job" or "google jobs" in low_src or "linkedin" in low_src or "naukri" in low_src:
            return cls.RELIABILITY_TABLE["google_jobs"]

        # Check for forum domains
        if any(f in low_url or f in low_src for f in cls.FORUM_DOMAINS):
            return cls.RELIABILITY_TABLE["forum"]

        # Check for major verified news outlets
        if any(news in low_url or news in low_src for news in cls.MAJOR_NEWS_DOMAINS) or source_type == "news":
            return cls.RELIABILITY_TABLE["major_news"]

        # Official company / careers page
        if "careers." in low_url or "jobs." in low_url or "/careers" in low_url or "/jobs" in low_url:
            return cls.RELIABILITY_TABLE["official_company"]

        # Local Maps verification
        if source_type == "local":
            return 80.0

        # Trends index from Google
        if source_type == "trend":
            return 85.0

        if source_type == "web":
            return cls.RELIABILITY_TABLE["general_web"]

        return cls.RELIABILITY_TABLE["default"]


class RelevanceEngine:
    """Evaluates evidence relevance and computes composite evidence strength."""

    STOP_WORDS = {
        "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are",
        "which", "best", "what", "where", "how", "with", "by", "from", "as", "about"
    }

    INTENT_KEYWORDS = {
        "career": {"job", "jobs", "career", "hiring", "salary", "engineer", "entry-level", "junior", "role", "tech", "openings", "recruiting"},
        "company": {"company", "startup", "firm", "enterprise", "funding", "layoff", "expansion", "growth", "headcount", "hiring"},
        "technology": {"technology", "stack", "framework", "library", "adoption", "skill", "learning", "developer", "engineering"},
    }

    @classmethod
    def _tokenize(cls, text: Optional[str]) -> set[str]:
        if not text:
            return set()
        words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        return {w for w in words if w not in cls.STOP_WORDS and len(w) > 1}

    @classmethod
    def calculate_relevance(
        cls,
        evidence: NormalizedEvidence,
        query: str,
        target_location: Optional[str] = None,
        intent: Optional[str] = "career",
    ) -> float:
        """Calculate relevance score (0-100) using multi-factor signals:

        1. Query token overlap (40%)
        2. Semantic intent alignment (25%)
        3. Location match (20%)
        4. Channel / entity specificity (15%)
        """
        combined_text = f"{evidence.title or ''} {evidence.snippet or ''} {evidence.source or ''} {evidence.entity or ''}".lower()
        content_tokens = cls._tokenize(combined_text)

        # 1. Query Keyword Match (Weight: 40)
        query_tokens = cls._tokenize(query)
        if query_tokens:
            overlap = query_tokens.intersection(content_tokens)
            keyword_score = (len(overlap) / len(query_tokens)) * 100.0
        else:
            keyword_score = 50.0

        # 2. Intent Match (Weight: 25)
        intent_vocab = cls.INTENT_KEYWORDS.get(intent or "career", cls.INTENT_KEYWORDS["career"])
        intent_hits = len(intent_vocab.intersection(content_tokens))
        intent_score = min(100.0, intent_hits * 25.0)

        # 3. Location Match (Weight: 20)
        location_score = 0.0
        if target_location:
            loc_lower = target_location.lower()
            if evidence.location and loc_lower in evidence.location.lower():
                location_score = 100.0
            elif loc_lower in combined_text:
                location_score = 85.0
            else:
                location_score = 30.0
        else:
            location_score = 75.0  # neutral if query is location-agnostic

        # 4. Source Specificity (Weight: 15)
        specificity_score = 60.0
        if evidence.source_type == "job" and (intent == "career" or "career" in query.lower() or "job" in query.lower()):
            specificity_score = 95.0
        elif evidence.source_type == "trend":
            specificity_score = 80.0
        elif evidence.entity and len(evidence.entity) > 2:
            specificity_score = 85.0

        # Composite Relevance calculation
        relevance = (
            0.40 * keyword_score +
            0.25 * intent_score +
            0.20 * location_score +
            0.15 * specificity_score
        )

        return round(max(0.0, min(100.0, relevance)), 1)

    @classmethod
    def evaluate(
        cls,
        evidence: NormalizedEvidence,
        query: str,
        target_location: Optional[str] = None,
        intent: Optional[str] = "career",
    ) -> NormalizedEvidence:
        """Score evidence relevance, freshness, reliability, and composite strength."""
        # Calculate individual scores
        relevance = cls.calculate_relevance(evidence, query, target_location, intent)
        freshness = FreshnessEngine.calculate_score(evidence.published_at)
        reliability = ReliabilityScorer.calculate_reliability(evidence.source, evidence.source_type, evidence.url)

        # Evidence Strength: 0.5 * relevance + 0.3 * freshness + 0.2 * reliability
        strength = (0.5 * relevance) + (0.3 * freshness) + (0.2 * reliability)
        strength = round(max(0.0, min(100.0, strength)), 1)

        evidence.relevance_score = relevance
        evidence.freshness_score = freshness
        evidence.reliability_score = reliability
        evidence.evidence_strength = strength

        return evidence
