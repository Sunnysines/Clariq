"""Evidence Agreement & Confidence Engine.

Evaluates independent cross-channel corroboration and source diversity to compute
explainable Clariq Confidence Scores.
"""
from __future__ import annotations

import urllib.parse
from typing import Literal, Optional
from pydantic import BaseModel, Field

from app.schemas.evidence import NormalizedEvidence
from app.services.signal_engine import DecisionSignal

ConfidenceLevel = Literal["HIGH", "MEDIUM", "LOW"]


class ConfidenceExplanation(BaseModel):
    """Structured, explainable Clariq confidence assessment."""

    score: float  # 0 to 100
    level: ConfidenceLevel
    reasons: list[str] = Field(default_factory=list)
    channels_detected: list[str] = Field(default_factory=list)
    distinct_sources_count: int = 0
    evidence_ids: list[str] = Field(default_factory=list)


class AgreementEngine:
    """Calculates cross-engine corroboration and source diversity."""

    @staticmethod
    def _extract_domain(url_or_source: Optional[str]) -> Optional[str]:
        if not url_or_source:
            return None
        if "://" in url_or_source:
            try:
                parsed = urllib.parse.urlparse(url_or_source)
                return parsed.netloc.lower().replace("www.", "")
            except Exception:
                pass
        return url_or_source.lower().strip()

    @classmethod
    def calculate_confidence(
        cls,
        evidence_items: list[NormalizedEvidence],
        signals: Optional[list[DecisionSignal]] = None,
        has_contradictions: bool = False,
    ) -> ConfidenceExplanation:
        """Compute Clariq Confidence Score (0-100) and qualitative level (HIGH / MEDIUM / LOW).

        Considerations:
        - Source diversity (Jobs, News, Web, Trends, Maps)
        - Independent domain count (no single-source echo chambers)
        - Mean evidence strength
        - Recency / temporal validity
        - Contradiction damping
        """
        if not evidence_items:
            return ConfidenceExplanation(
                score=20.0,
                level="LOW",
                reasons=["No verified evidence records available."],
                channels_detected=[],
                distinct_sources_count=0,
                evidence_ids=[],
            )

        evidence_ids = [e.id for e in evidence_items if e.id]
        reasons: list[str] = []

        # 1. Channel Diversity (max 35 points)
        channels = {e.source_type for e in evidence_items}
        channels_detected = sorted(list(channels))
        chan_count = len(channels)

        if chan_count >= 4:
            chan_score = 35.0
            reasons.append(f"Supported across {chan_count} distinct evidence channels ({', '.join(channels_detected)})")
        elif chan_count == 3:
            chan_score = 28.0
            reasons.append(f"Cross-verified across 3 channels ({', '.join(channels_detected)})")
        elif chan_count == 2:
            chan_score = 20.0
            reasons.append(f"Corroborated across 2 channels ({', '.join(channels_detected)})")
        else:
            chan_score = 10.0
            single_ch = channels_detected[0] if channels_detected else "single channel"
            reasons.append(f"Single evidence channel only ({single_ch}) — lacks cross-platform verification")

        # 2. Distinct Domains / Independent Sources (max 20 points)
        domains = set()
        for e in evidence_items:
            d = cls._extract_domain(e.url) or cls._extract_domain(e.source)
            if d:
                domains.add(d)

        domain_count = len(domains)
        if domain_count >= 4:
            domain_score = 20.0
            reasons.append(f"Multiple independent sources agree ({domain_count} distinct publishers/domains)")
        elif domain_count >= 2:
            domain_score = 14.0
            reasons.append(f"{domain_count} independent sources represented")
        else:
            domain_score = 7.0
            reasons.append("Limited source diversity — evidence stems from solitary publisher")

        # 3. Evidence Strength (max 25 points)
        avg_strength = sum(e.evidence_strength or 70.0 for e in evidence_items) / len(evidence_items)
        strength_score = (avg_strength / 100.0) * 25.0

        # 4. Recency (max 10 points)
        fresh_count = sum(1 for e in evidence_items if (e.freshness_score or 0) >= 90.0)
        fresh_ratio = fresh_count / len(evidence_items) if evidence_items else 0
        recency_score = fresh_ratio * 10.0
        if fresh_ratio >= 0.4:
            reasons.append("Evidence is highly recent (within 7 days)")

        # 5. Volume (max 10 points)
        vol_score = min(10.0, len(evidence_items) * 1.0)

        # Base score before penalties
        raw_score = chan_score + domain_score + strength_score + recency_score + vol_score

        # 6. Contradiction Penalty
        contradiction_penalty = 0.0
        if has_contradictions:
            contradiction_penalty = 15.0
            reasons.append("Confidence dampened due to detected conflicting signals")

        final_score = round(max(10.0, min(100.0, raw_score - contradiction_penalty)), 1)

        # Categorize Level
        if final_score >= 80.0:
            level: ConfidenceLevel = "HIGH"
        elif final_score >= 55.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return ConfidenceExplanation(
            score=final_score,
            level=level,
            reasons=reasons,
            channels_detected=channels_detected,
            distinct_sources_count=domain_count,
            evidence_ids=evidence_ids,
        )
