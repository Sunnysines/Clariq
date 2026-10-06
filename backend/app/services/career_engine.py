"""Career Intelligence Decision Engine.

Flagship mode: Evaluates open-ended career questions (e.g., "Which Indian city is best
for an entry-level AI/ML career in 2026?") across target cities using live SerpApi multi-engine evidence.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.evidence import NormalizedEvidence
from app.services.serpapi.orchestrator import SearchOrchestrator, EngineSearchInstruction
from app.services.evidence_engine import EvidenceEngine
from app.services.relevance_engine import RelevanceEngine
from app.services.entity_resolver import EntityResolver
from app.services.signal_engine import SignalEngine, DecisionSignal
from app.services.agreement_engine import AgreementEngine, ConfidenceExplanation
from app.services.contradiction_engine import ContradictionEngine, ContradictionRecord

logger = logging.getLogger("clariq.career_engine")


class CategoryScores(BaseModel):
    """5-dimension category scoring for career intelligence (Clariq Product Assumptions)."""
    job_opportunity: float = 0.0     # 35% weight
    market_demand: float = 0.0       # 20% weight
    recent_activity: float = 0.0     # 20% weight
    company_presence: float = 0.0    # 15% weight
    evidence_confidence: float = 0.0 # 10% weight


class ScoreContribution(BaseModel):
    label: str
    score_contribution: float
    evidence_count: int
    direction: str  # positive | negative
    evidence_ids: list[str] = Field(default_factory=list)


class CityDecisionResult(BaseModel):
    city: str
    overall_score: float
    rank: int = 1
    category_scores: CategoryScores
    signals: list[DecisionSignal] = Field(default_factory=list)
    contradictions: list[ContradictionRecord] = Field(default_factory=list)
    confidence: float
    confidence_level: str
    confidence_reasons: list[str] = Field(default_factory=list)
    evidence_count: int
    evidence_ids: list[str] = Field(default_factory=list)


class CareerAnalysisOutput(BaseModel):
    analysis_id: str
    question: str
    mode: str = "career"
    cities: list[CityDecisionResult]
    top_city: str
    recommendation: dict[str, Any]
    explanation: dict[str, Any]
    statistics: dict[str, int]


class CareerEngine:
    """Executes the full career decision pipeline across candidate cities."""

    DEFAULT_CITIES = ["Bengaluru", "Hyderabad", "Pune", "Chennai"]

    # Clariq Product Scoring Assumptions
    WEIGHTS = {
        "job_opportunity": 0.35,
        "market_demand": 0.20,
        "recent_activity": 0.20,
        "company_presence": 0.15,
        "evidence_confidence": 0.10,
    }

    def __init__(self, orchestrator: Optional[SearchOrchestrator] = None):
        self.orchestrator = orchestrator or SearchOrchestrator()
        self.evidence_engine = EvidenceEngine()

    def build_search_plan(
        self,
        question: str,
        target_cities: list[str],
    ) -> list[EngineSearchInstruction]:
        """Generate targeted multi-engine search instructions for each city."""
        instructions: list[EngineSearchInstruction] = []

        # National trends query
        instructions.append(
            EngineSearchInstruction(engine="google_trends", query="AI engineer jobs", geo="IN")
        )

        for city in target_cities:
            # 1. Google Jobs
            instructions.append(
                EngineSearchInstruction(
                    engine="google_jobs",
                    query=f"entry level AI ML engineer in {city}",
                    location=city,
                )
            )
            # 2. Google Search (career ecosystem)
            instructions.append(
                EngineSearchInstruction(
                    engine="google_search",
                    query=f"entry level AI ML career ecosystem {city} 2026",
                    location=city,
                    num=8,
                )
            )
            # 3. Google News (tech hiring and company investments)
            instructions.append(
                EngineSearchInstruction(
                    engine="google_news",
                    query=f"AI tech hiring {city}",
                    location=city,
                )
            )
            # 4. Google Local (tech parks and innovation centers)
            instructions.append(
                EngineSearchInstruction(
                    engine="google_local",
                    query=f"AI research labs and tech parks in {city}",
                    location=city,
                )
            )

        return instructions

    async def analyze(
        self,
        question: str,
        analysis_id: Optional[str] = None,
        target_cities: Optional[list[str]] = None,
        on_stage_update: Optional[Any] = None,
    ) -> CareerAnalysisOutput:
        """Run the end-to-end evidence collection and scoring pipeline."""
        an_id = analysis_id or str(uuid.uuid4())
        cities = target_cities or self.DEFAULT_CITIES

        if on_stage_update:
            await on_stage_update("planning")

        # 1. Build and execute search plan
        instructions = self.build_search_plan(question, cities)
        if on_stage_update:
            await on_stage_update("searching_jobs")

        orch_res = await self.orchestrator.execute_plan(instructions)

        # 2. Normalize evidence
        if on_stage_update:
            await on_stage_update("normalizing")

        all_evidence: list[NormalizedEvidence] = []
        for report in orch_res.reports:
            norm_items = self.evidence_engine.normalize_report(
                report, analysis_id=an_id, location=report.query
            )
            for item in norm_items:
                scored = RelevanceEngine.evaluate(item, query=question, intent="career")
                all_evidence.append(scored)

        # 3. Resolve entities by city
        if on_stage_update:
            await on_stage_update("resolving_entities")

        city_evidence_map: dict[str, list[NormalizedEvidence]] = {c: [] for c in cities}
        for ev in all_evidence:
            text = f"{ev.title or ''} {ev.snippet or ''} {ev.location or ''}".lower()
            for c in cities:
                aliases = EntityResolver.CITY_ALIASES.get(c, {c.lower()})
                if any(a in text for a in aliases):
                    city_evidence_map[c].append(ev)

        # Also distribute trend evidence to all candidate cities
        trend_items = [e for e in all_evidence if e.source_type == "trend"]
        for c in cities:
            for t in trend_items:
                if t not in city_evidence_map[c]:
                    city_evidence_map[c].append(t)

        # 4. Analyze signals, contradictions, and calculate category scores per city
        if on_stage_update:
            await on_stage_update("analyzing_signals")

        city_results: list[CityDecisionResult] = []
        all_signals_count = 0
        all_conflicts_count = 0

        for city in cities:
            ev_list = city_evidence_map.get(city, [])
            signals = SignalEngine.extract_signals_for_entity(ev_list, entity_name=city, analysis_id=an_id)
            all_signals_count += len(signals)

            conflict_summary = ContradictionEngine.detect_conflicts_for_entity(signals, entity_name=city, analysis_id=an_id)
            all_conflicts_count += len(conflict_summary.conflicts)

            conf_explanation = AgreementEngine.calculate_confidence(
                ev_list, signals=signals, has_contradictions=conflict_summary.has_conflict
            )

            # Category 1: Job Opportunity (35%)
            job_items = [e for e in ev_list if e.source_type == "job"]
            job_strength_avg = sum(e.evidence_strength or 70.0 for e in job_items) / len(job_items) if job_items else 40.0
            job_score = min(100.0, (len(job_items) * 6.0) + (job_strength_avg * 0.4))
            job_score = round(max(30.0, job_score), 1)

            # Category 2: Market Demand (20%)
            demand_sigs = [s for s in signals if s.type in ("DEMAND", "POPULARITY")]
            demand_score = sum(s.strength for s in demand_sigs) / len(demand_sigs) if demand_sigs else 60.0
            demand_score = round(min(100.0, demand_score), 1)

            # Category 3: Recent Activity (20%)
            recent_items = [e for e in ev_list if (e.freshness_score or 0) >= 80.0]
            activity_score = min(100.0, (len(recent_items) * 7.0) + 40.0) if recent_items else 50.0
            activity_score = round(activity_score, 1)

            # Category 4: Company Presence (15%)
            company_names = {e.entity for e in ev_list if e.entity and e.entity != city}
            company_score = min(100.0, (len(company_names) * 8.0) + 45.0)
            company_score = round(company_score, 1)

            # Category 5: Evidence Confidence (10%)
            evidence_confidence = conf_explanation.score

            # Composite Overall Score (weighted sum)
            composite = (
                self.WEIGHTS["job_opportunity"] * job_score +
                self.WEIGHTS["market_demand"] * demand_score +
                self.WEIGHTS["recent_activity"] * activity_score +
                self.WEIGHTS["company_presence"] * company_score +
                self.WEIGHTS["evidence_confidence"] * evidence_confidence
            )

            # Apply contradiction damper if high severity conflict exists
            if conflict_summary.severity == "high":
                composite -= 4.0

            overall = round(max(20.0, min(100.0, composite)), 1)

            cat_scores = CategoryScores(
                job_opportunity=job_score,
                market_demand=demand_score,
                recent_activity=activity_score,
                company_presence=company_score,
                evidence_confidence=evidence_confidence,
            )

            city_results.append(
                CityDecisionResult(
                    city=city,
                    overall_score=overall,
                    category_scores=cat_scores,
                    signals=signals,
                    contradictions=conflict_summary.conflicts,
                    confidence=conf_explanation.score,
                    confidence_level=conf_explanation.level,
                    confidence_reasons=conf_explanation.reasons,
                    evidence_count=len(ev_list),
                    evidence_ids=[e.id for e in ev_list if e.id],
                )
            )

        # 5. Rank cities by overall score
        city_results.sort(key=lambda x: x.overall_score, reverse=True)
        for idx, cr in enumerate(city_results):
            cr.rank = idx + 1

        top_city = city_results[0]

        # 6. Build Explainable Why Contributions
        top_city_evs = city_evidence_map.get(top_city.city, [])
        top_jobs_count = len([e for e in top_city_evs if e.source_type == "job"])
        top_companies = {e.entity for e in top_city_evs if e.entity and e.entity != top_city.city}

        contributions: list[ScoreContribution] = [
            ScoreContribution(
                label=f"{top_jobs_count} verified job listings and recruitment channels",
                score_contribution=round(top_city.category_scores.job_opportunity * 0.35, 1),
                evidence_count=top_jobs_count,
                direction="positive",
                evidence_ids=[e.id for e in top_city_evs if e.source_type == "job" and e.id],
            ),
            ScoreContribution(
                label=f"{len(top_companies)} technology and AI entities detected",
                score_contribution=round(top_city.category_scores.company_presence * 0.15, 1),
                evidence_count=len(top_companies),
                direction="positive",
                evidence_ids=[e.id for e in top_city_evs if e.entity and e.id],
            ),
            ScoreContribution(
                label="Sustained search volume and market talent demand",
                score_contribution=round(top_city.category_scores.market_demand * 0.20, 1),
                evidence_count=len([e for e in top_city_evs if e.source_type == "trend"]),
                direction="positive",
                evidence_ids=[e.id for e in top_city_evs if e.source_type == "trend" and e.id],
            ),
        ]

        if top_city.contradictions:
            contributions.append(
                ScoreContribution(
                    label="Conflicting signals detected in selective hiring areas",
                    score_contribution=-4.0,
                    evidence_count=len(top_city.contradictions[0].evidence_ids),
                    direction="negative",
                    evidence_ids=top_city.contradictions[0].evidence_ids,
                )
            )

        if on_stage_update:
            await on_stage_update("recommending")

        return CareerAnalysisOutput(
            analysis_id=an_id,
            question=question,
            mode="career",
            cities=city_results,
            top_city=top_city.city,
            recommendation={
                "top_city": top_city.city,
                "score": top_city.overall_score,
                "confidence": top_city.confidence,
                "confidence_level": top_city.confidence_level,
                "summary": (
                    f"{top_city.city} ranks first for entry-level AI/ML careers with an overall score "
                    f"of {top_city.overall_score}/100 and {top_city.confidence_level} confidence. "
                    f"It exhibits highest opportunity density across verified job listings and employer ecosystem."
                ),
                "reasons": [
                    f"Highest job opportunity density ({top_city.category_scores.job_opportunity}%)",
                    f"Strong corporate tech ecosystem ({top_city.category_scores.company_presence}%)",
                    f"Supported by {top_city.evidence_count} multi-channel evidence items",
                ],
                "actions": [
                    f"Focus your job search on {top_city.city}",
                    "Prioritize top detected AI hiring companies",
                    "Inspect high-confidence job postings in the Evidence Explorer",
                    "Audit conflicting signals before committing to specific firms",
                ],
            },
            explanation={
                "contributions": [c.model_dump() for c in contributions],
                "scoring_weights_explanation": (
                    "Scores are calculated using Clariq's transparent weights: "
                    "Job Opportunity (35%), Market Demand (20%), Recent Activity (20%), "
                    "Company Presence (15%), Evidence Confidence (10%)."
                ),
            },
            statistics={
                "total_evidence": len(all_evidence),
                "total_searches": len(instructions),
                "total_entities": len(cities),
                "total_signals": all_signals_count,
                "total_contradictions": all_conflicts_count,
            },
        )
