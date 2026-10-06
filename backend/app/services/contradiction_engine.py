"""Contradiction Detection Engine.

Surfaces and categorizes conflicting signals regarding the same entity (e.g., active hiring
juxtaposed against workforce reductions or hiring freezes), ensuring transparency.
"""
from __future__ import annotations

import uuid
from typing import Literal, Optional
from pydantic import BaseModel, Field

from app.services.signal_engine import DecisionSignal

SeverityLevel = Literal["low", "medium", "high"]


class ContradictionRecord(BaseModel):
    """Specific detected conflict pair between positive and negative signals."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    entity_id: Optional[str] = None
    entity_name: str
    positive_signal: str
    negative_signal: str
    severity: SeverityLevel
    confidence: float  # 0 to 100
    description: str
    evidence_ids: list[str] = Field(default_factory=list)


class ContradictionSummary(BaseModel):
    """High-level summary of entity conflicts for UI presentation."""

    has_conflict: bool
    severity: Optional[SeverityLevel] = None
    summary: str
    conflicts: list[ContradictionRecord] = Field(default_factory=list)


class ContradictionEngine:
    """Detects, validates, and grades semantic conflicts across entity signals."""

    # Signal pairs that legitimately contradict when opposed
    CONTRADICTION_MAP = {
        ("HIRING", "RISK"): {
            "description": "Active recruitment drives co-occur with reports of layoffs or hiring freezes.",
            "base_severity": "high",
        },
        ("GROWTH", "RISK"): {
            "description": "Reported market/headcount expansion conflicts with workforce restructuring or downsizing.",
            "base_severity": "medium",
        },
        ("DEMAND", "RISK"): {
            "description": "Acute skill shortages exist alongside organizational cost-cutting measures.",
            "base_severity": "medium",
        },
        ("HIRING", "COMPETITION"): {
            "description": "Open role volume is offset by severe applicant saturation and hiring hurdles.",
            "base_severity": "low",
        },
    }

    @classmethod
    def detect_conflicts_for_entity(
        cls,
        signals: list[DecisionSignal],
        entity_name: str,
        analysis_id: str,
        entity_id: Optional[str] = None,
    ) -> ContradictionSummary:
        """Scan signals for an entity and detect opposing evidence clusters."""
        positives = [s for s in signals if s.direction == "positive"]
        negatives = [s for s in signals if s.direction == "negative"]

        if not positives or not negatives:
            return ContradictionSummary(
                has_conflict=False,
                severity=None,
                summary=f"No conflicting signals detected for {entity_name}.",
                conflicts=[],
            )

        conflicts: list[ContradictionRecord] = []

        for p in positives:
            for n in negatives:
                pair = (p.type, n.type)
                if pair not in cls.CONTRADICTION_MAP:
                    continue

                rule = cls.CONTRADICTION_MAP[pair]
                base_sev: SeverityLevel = rule["base_severity"]

                # Determine actual severity based on signal strengths
                if p.strength >= 75.0 and n.strength >= 75.0:
                    severity: SeverityLevel = "high"
                elif p.strength < 50.0 or n.strength < 50.0:
                    severity = "low"
                else:
                    severity = base_sev

                # Combined confidence in the contradiction existing
                conflict_confidence = round(min(100.0, (p.strength + n.strength) / 2.0), 1)

                # Merge distinct evidence IDs
                combined_ev_ids = list(dict.fromkeys((p.evidence_ids or []) + (n.evidence_ids or [])))

                desc = (
                    f"Conflict detected for {entity_name}: {rule['description']} "
                    f"({p.description} vs {n.description})"
                )

                conflicts.append(
                    ContradictionRecord(
                        analysis_id=analysis_id,
                        entity_id=entity_id,
                        entity_name=entity_name,
                        positive_signal=f"[{p.type}] {p.description}",
                        negative_signal=f"[{n.type}] {n.description}",
                        severity=severity,
                        confidence=conflict_confidence,
                        description=desc,
                        evidence_ids=combined_ev_ids,
                    )
                )

        if not conflicts:
            return ContradictionSummary(
                has_conflict=False,
                severity=None,
                summary=f"No substantive semantic contradictions found for {entity_name}.",
                conflicts=[],
            )

        # Determine overall severity
        has_high = any(c.severity == "high" for c in conflicts)
        has_med = any(c.severity == "medium" for c in conflicts)
        top_severity: SeverityLevel = "high" if has_high else ("medium" if has_med else "low")

        if top_severity == "high":
            summary_text = (
                f"Significant contradiction: Strong positive signals ({len(positives)}) "
                f"exist alongside verified workforce reductions or risks for {entity_name}."
            )
        else:
            summary_text = (
                f"Moderate contradiction: Selective hiring or demand indicators exist alongside "
                f"restructuring reports for {entity_name}."
            )

        return ContradictionSummary(
            has_conflict=True,
            severity=top_severity,
            summary=summary_text,
            conflicts=conflicts,
        )
