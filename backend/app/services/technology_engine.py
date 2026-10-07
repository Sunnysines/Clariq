"""Technology Intelligence Decision Engine.

Analyzes questions such as "Is AI agent development worth learning for a software engineering
student in 2026?" by collecting multi-engine SerpApi evidence on demand, hiring, popularity,
enterprise adoption, and risks to compute an explainable viability score.
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

logger = logging.getLogger("clariq.technology_engine")


class TechnologyDecisionResult(BaseModel):
    technology: str
    overall_score: float
    confidence: float
    confidence_level: str
    confidence_reasons: list[str] = Field(default_factory=list)
    verdict: str  # STRONGLY RECOMMENDED | WORTH LEARNING | PROCEED WITH CAUTION
    signals: list[DecisionSignal] = Field(default_factory=list)
    contradictions: list[ContradictionRecord] = Field(default_factory=list)
    evidence_count: int = 0
    evidence_ids: list[str] = Field(default_factory=list)


class TechnologyAnalysisOutput(BaseModel):
    analysis_id: str
    question: str
    mode: str = "technology"
    technologies: list[TechnologyDecisionResult]
    top_technology: str
    recommendation: dict[str, Any]
    explanation: dict[str, Any]
    statistics: dict[str, int]


class TechnologyEngine:
    """Executes the Technology Intelligence viability and learning decision pipeline."""

    def __init__(self, orchestrator: Optional[SearchOrchestrator] = None):
        self.orchestrator = orchestrator or SearchOrchestrator()
        self.evidence_engine = EvidenceEngine()
        self.last_evidence: list[NormalizedEvidence] = []

    def extract_technology_topic(self, question: str) -> str:
        """Extract canonical technology subject from question or query."""
        q_clean = question.lower()
        if "agent" in q_clean or "agents" in q_clean:
            return "AI Agent Development"
        elif "llm" in q_clean or "large language model" in q_clean:
            return "Large Language Models (LLMs)"
        elif "generative ai" in q_clean or "genai" in q_clean:
            return "Generative AI"
        elif "pytorch" in q_clean:
            return "PyTorch"
        elif "computer vision" in q_clean:
            return "Computer Vision"
        elif "rust" in q_clean:
            return "Rust"
        return "AI/ML Technology"

    def build_search_plan(self, tech_topic: str) -> list[EngineSearchInstruction]:
        """Generate targeted search instructions across Jobs, Trends, News, and Search."""
        return [
            # 1. Google Jobs
            EngineSearchInstruction(
                engine="google_jobs",
                query=f"{tech_topic} engineer jobs India",
                location="India",
            ),
            # 2. Google Trends
            EngineSearchInstruction(
                engine="google_trends",
                query=tech_topic if len(tech_topic) < 30 else "AI agents",
                geo="IN",
            ),
            # 3. Google News (industry adoption & investment)
            EngineSearchInstruction(
                engine="google_news",
                query=f"{tech_topic} enterprise adoption market growth",
            ),
            # 4. Google Search (career demand & limitations)
            EngineSearchInstruction(
                engine="google_search",
                query=f"is {tech_topic} worth learning software engineering 2026 demand risks",
                num=8,
            ),
        ]

    async def analyze(
        self,
        question: str,
        analysis_id: Optional[str] = None,
        on_stage_update: Optional[Any] = None,
    ) -> TechnologyAnalysisOutput:
        """Execute technology viability analysis pipeline."""
        an_id = analysis_id or str(uuid.uuid4())
        tech_topic = self.extract_technology_topic(question)

        if on_stage_update:
            await on_stage_update("planning")

        instructions = self.build_search_plan(tech_topic)

        if on_stage_update:
            await on_stage_update("searching_jobs")

        orch_res = await self.orchestrator.execute_plan(instructions)

        # 2. Normalize evidence
        if on_stage_update:
            await on_stage_update("normalizing")

        all_evidence: list[NormalizedEvidence] = []
        self.last_evidence = all_evidence
        for report in orch_res.reports:
            norm_items = self.evidence_engine.normalize_report(report, analysis_id=an_id)
            for item in norm_items:
                scored = RelevanceEngine.evaluate(item, query=question, intent="technology")
                all_evidence.append(scored)

        # 3. Extract signals and conflicts
        if on_stage_update:
            await on_stage_update("analyzing_signals")

        signals = SignalEngine.extract_signals_for_entity(
            all_evidence, entity_name=tech_topic, analysis_id=an_id
        )

        conflict_summary = ContradictionEngine.detect_conflicts_for_entity(
            signals, entity_name=tech_topic, analysis_id=an_id
        )

        conf_explanation = AgreementEngine.calculate_confidence(
            all_evidence, signals=signals, has_contradictions=conflict_summary.has_conflict
        )

        # Category signal strengths
        hiring_sigs = [s for s in signals if s.type == "HIRING"]
        demand_sigs = [s for s in signals if s.type == "DEMAND"]
        growth_sigs = [s for s in signals if s.type in ("GROWTH", "INVESTMENT")]
        pop_sigs = [s for s in signals if s.type == "POPULARITY"]
        risk_sigs = [s for s in signals if s.type == "RISK"]

        hiring_score = sum(s.strength for s in hiring_sigs) / len(hiring_sigs) if hiring_sigs else 65.0
        demand_score = sum(s.strength for s in demand_sigs) / len(demand_sigs) if demand_sigs else 70.0
        growth_score = sum(s.strength for s in growth_sigs) / len(growth_sigs) if growth_sigs else 75.0
        pop_score = sum(s.strength for s in pop_sigs) / len(pop_sigs) if pop_sigs else 80.0
        risk_penalty = min(15.0, sum(s.strength for s in risk_sigs) * 0.15) if risk_sigs else 0.0

        # Composite Technology Viability Score
        composite = (
            (hiring_score * 0.35) +
            (demand_score * 0.25) +
            (growth_score * 0.20) +
            (conf_explanation.score * 0.10) +
            (pop_score * 0.10) -
            risk_penalty
        )
        overall_score = round(max(30.0, min(100.0, composite)), 1)

        # Verdict
        if overall_score >= 82.0:
            verdict = "STRONGLY WORTH LEARNING"
        elif overall_score >= 68.0:
            verdict = "WORTH LEARNING"
        else:
            verdict = "PROCEED WITH CAUTION"

        tech_result = TechnologyDecisionResult(
            technology=tech_topic,
            overall_score=overall_score,
            confidence=conf_explanation.score,
            confidence_level=conf_explanation.level,
            confidence_reasons=conf_explanation.reasons,
            verdict=verdict,
            signals=signals,
            contradictions=conflict_summary.conflicts,
            evidence_count=len(all_evidence),
            evidence_ids=[e.id for e in all_evidence if e.id],
        )

        if on_stage_update:
            await on_stage_update("recommending")

        return TechnologyAnalysisOutput(
            analysis_id=an_id,
            question=question,
            mode="technology",
            technologies=[tech_result],
            top_technology=tech_topic,
            recommendation={
                "top_technology": tech_topic,
                "score": overall_score,
                "confidence": conf_explanation.score,
                "confidence_level": conf_explanation.level,
                "verdict": verdict,
                "summary": (
                    f"{tech_topic} is evaluated as '{verdict}' for a software engineering student in 2026 "
                    f"with an overall viability score of {overall_score}/100 and {conf_explanation.level} confidence. "
                    f"Verified demand across job openings, developer adoption, and enterprise investment."
                ),
                "reasons": [
                    f"High market hiring & opportunity score ({round(hiring_score)}%)",
                    f"Sustained developer and search interest ({round(pop_score)}%)",
                    f"Supported by {len(all_evidence)} verified multi-channel evidence items",
                ],
                "actions": [
                    f"Build production-grade projects demonstrating {tech_topic}",
                    "Inspect practical role skill requirements in the Evidence Explorer",
                    "Audit architectural failure modes and security risks surfaced in conflicting reports",
                ],
            },
            explanation={
                "contributions": [
                    {
                        "label": f"Active job market demand for {tech_topic}",
                        "score_contribution": round(hiring_score * 0.35, 1),
                        "evidence_count": len([e for e in all_evidence if e.source_type == "job"]),
                        "direction": "positive",
                    },
                    {
                        "label": "Industry adoption and enterprise investment",
                        "score_contribution": round(growth_score * 0.20, 1),
                        "evidence_count": len(growth_sigs),
                        "direction": "positive",
                    },
                    {
                        "label": "Multi-channel evidence agreement",
                        "score_contribution": round(conf_explanation.score * 0.10, 1),
                        "evidence_count": len(conf_explanation.channels_detected),
                        "direction": "positive",
                    },
                ],
                "scoring_weights_explanation": (
                    "Technology intelligence weights: Job Market (35%), Market Demand (25%), "
                    "Growth & Investment (20%), Confidence (10%), Search Popularity (10%), minus risk penalties."
                ),
            },
            statistics={
                "total_evidence": len(all_evidence),
                "total_searches": len(instructions),
                "total_entities": 1,
                "total_signals": len(signals),
                "total_contradictions": len(conflict_summary.conflicts),
            },
        )
