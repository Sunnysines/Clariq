"""Signal Engine – transforms verified evidence into interpretable decision indicators.

Derives signals strictly from retrieved evidence records:
- HIRING
- DEMAND
- GROWTH
- INVESTMENT
- POPULARITY
- RECENCY
- COMPETITION
- RISK
"""
from __future__ import annotations

import re
import uuid
from typing import Literal, Optional
from pydantic import BaseModel, Field

from app.schemas.evidence import NormalizedEvidence

SignalType = Literal[
    "HIRING", "DEMAND", "GROWTH", "INVESTMENT", "POPULARITY", "RECENCY", "COMPETITION", "RISK"
]
SignalDirection = Literal["positive", "negative", "neutral"]


class DecisionSignal(BaseModel):
    """Interpretable decision indicator backed by verified evidence items."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    entity: str
    type: SignalType
    direction: SignalDirection
    strength: float  # 0 to 100
    evidence_count: int
    description: str
    evidence_ids: list[str] = Field(default_factory=list)


class SignalEngine:
    """Extracts, categorizes, and scores evidence-driven signals."""

    # Keyword dictionaries for signal pattern detection
    PATTERNS = {
        "RISK": re.compile(
            r"\b(?:layoff|laid off|downsizing|hiring freeze|cost-cutting|severance|"
            r"workforce reduction|headcount cut|redundancy|pink slips|slashing jobs)\b",
            re.IGNORECASE,
        ),
        "INVESTMENT": re.compile(
            r"\b(?:funding|series [a-d]|raised \$|invests|venture capital|infusion|"
            r"seed round|r&d center|new campus|inaugurates|investing crores|backed by)\b",
            re.IGNORECASE,
        ),
        "GROWTH": re.compile(
            r"\b(?:expanding|rapid growth|surging|scale-up|hiring surge|market expansion|"
            r"opening new office|doubling team|growth trajectory)\b",
            re.IGNORECASE,
        ),
        "DEMAND": re.compile(
            r"\b(?:high demand|talent shortage|urgent demand|strong demand|skills gap|"
            r"critical need|hot skill|most wanted)\b",
            re.IGNORECASE,
        ),
        "COMPETITION": re.compile(
            r"\b(?:highly competitive|talent surplus|stiff competition|oversubscribed|"
            r"thousands of applicants|competitive market)\b",
            re.IGNORECASE,
        ),
    }

    @classmethod
    def extract_signals_for_entity(
        cls,
        evidence_items: list[NormalizedEvidence],
        entity_name: str,
        analysis_id: str,
    ) -> list[DecisionSignal]:
        """Derive strictly evidence-backed signals for an entity."""
        if not evidence_items:
            return []

        signals: list[DecisionSignal] = []

        # 1. HIRING Signal (from Job postings or hiring text)
        job_evs = [e for e in evidence_items if e.source_type == "job"]
        hiring_text_evs = [
            e for e in evidence_items
            if e.source_type != "job" and re.search(r"\b(?:hiring|open positions|vacancies|job openings)\b", f"{e.title} {e.snippet}", re.I)
        ]
        all_hiring = job_evs + hiring_text_evs

        if all_hiring:
            count = len(all_hiring)
            ev_ids = [e.id for e in all_hiring if e.id]
            avg_strength = sum(e.evidence_strength or 70.0 for e in all_hiring) / count
            # Volume boost (diminishing return up to +15)
            vol_boost = min(15.0, count * 1.5)
            hiring_strength = round(min(100.0, avg_strength + vol_boost), 1)

            desc = f"{count} active hiring and job opportunity indicators detected for {entity_name}."
            if job_evs:
                desc = f"{len(job_evs)} verified job listings and {len(hiring_text_evs)} hiring mentions identified."

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="HIRING",
                    direction="positive",
                    strength=hiring_strength,
                    evidence_count=count,
                    description=desc,
                    evidence_ids=ev_ids,
                )
            )

        # 2. RISK Signal (from layoff, hiring freeze, reductions)
        risk_evs = [
            e for e in evidence_items
            if cls.PATTERNS["RISK"].search(f"{e.title or ''} {e.snippet or ''}")
        ]
        if risk_evs:
            count = len(risk_evs)
            ev_ids = [e.id for e in risk_evs if e.id]
            avg_strength = sum(e.evidence_strength or 70.0 for e in risk_evs) / count
            risk_strength = round(min(100.0, avg_strength + (count * 4.0)), 1)

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="RISK",
                    direction="negative",
                    strength=risk_strength,
                    evidence_count=count,
                    description=f"{count} risk reports regarding workforce adjustments or caution detected.",
                    evidence_ids=ev_ids,
                )
            )

        # 3. INVESTMENT Signal
        inv_evs = [
            e for e in evidence_items
            if cls.PATTERNS["INVESTMENT"].search(f"{e.title or ''} {e.snippet or ''}")
        ]
        if inv_evs:
            count = len(inv_evs)
            ev_ids = [e.id for e in inv_evs if e.id]
            avg_strength = sum(e.evidence_strength or 70.0 for e in inv_evs) / count
            inv_strength = round(min(100.0, avg_strength + (count * 3.0)), 1)

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="INVESTMENT",
                    direction="positive",
                    strength=inv_strength,
                    evidence_count=count,
                    description=f"{count} capital investment or ecosystem expansion announcements verified.",
                    evidence_ids=ev_ids,
                )
            )

        # 4. GROWTH Signal
        growth_evs = [
            e for e in evidence_items
            if cls.PATTERNS["GROWTH"].search(f"{e.title or ''} {e.snippet or ''}")
        ]
        if growth_evs:
            count = len(growth_evs)
            ev_ids = [e.id for e in growth_evs if e.id]
            avg_strength = sum(e.evidence_strength or 70.0 for e in growth_evs) / count
            growth_strength = round(min(100.0, avg_strength + (count * 2.5)), 1)

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="GROWTH",
                    direction="positive",
                    strength=growth_strength,
                    evidence_count=count,
                    description=f"{count} market expansion and positive headcount indicators detected.",
                    evidence_ids=ev_ids,
                )
            )

        # 5. DEMAND Signal
        demand_evs = [
            e for e in evidence_items
            if cls.PATTERNS["DEMAND"].search(f"{e.title or ''} {e.snippet or ''}")
        ]
        if demand_evs:
            count = len(demand_evs)
            ev_ids = [e.id for e in demand_evs if e.id]
            avg_strength = sum(e.evidence_strength or 70.0 for e in demand_evs) / count
            demand_strength = round(min(100.0, avg_strength + (count * 2.0)), 1)

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="DEMAND",
                    direction="positive",
                    strength=demand_strength,
                    evidence_count=count,
                    description=f"{count} indicators of acute market demand and skill shortages identified.",
                    evidence_ids=ev_ids,
                )
            )

        # 6. POPULARITY Signal (Google Trends or multi-source frequency)
        trend_evs = [e for e in evidence_items if e.source_type == "trend"]
        if trend_evs:
            count = len(trend_evs)
            ev_ids = [e.id for e in trend_evs if e.id]
            avg_strength = sum(e.evidence_strength or 75.0 for e in trend_evs) / count
            pop_strength = round(min(100.0, avg_strength), 1)

            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="POPULARITY",
                    direction="positive",
                    strength=pop_strength,
                    evidence_count=count,
                    description=f"Google Trends confirms sustained relative search volume for {entity_name}.",
                    evidence_ids=ev_ids,
                )
            )

        # 7. RECENCY Signal (Evidence within last 3 days)
        fresh_evs = [e for e in evidence_items if (e.freshness_score or 0) >= 90.0]
        if len(fresh_evs) >= 2:
            count = len(fresh_evs)
            ev_ids = [e.id for e in fresh_evs if e.id]
            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="RECENCY",
                    direction="positive",
                    strength=92.0,
                    evidence_count=count,
                    description=f"Recent market activity corroborated by {count} high-freshness items.",
                    evidence_ids=ev_ids,
                )
            )

        # 8. COMPETITION Signal
        comp_evs = [
            e for e in evidence_items
            if cls.PATTERNS["COMPETITION"].search(f"{e.title or ''} {e.snippet or ''}")
        ]
        if comp_evs:
            count = len(comp_evs)
            ev_ids = [e.id for e in comp_evs if e.id]
            signals.append(
                DecisionSignal(
                    analysis_id=analysis_id,
                    entity=entity_name,
                    type="COMPETITION",
                    direction="negative",
                    strength=75.0,
                    evidence_count=count,
                    description=f"Market indicators show heightened talent competition density in {entity_name}.",
                    evidence_ids=ev_ids,
                )
            )

        return signals
