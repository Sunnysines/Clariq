"""Unit tests for Technology Intelligence Decision Engine."""
from unittest.mock import AsyncMock
import pytest

from app.services.technology_engine import TechnologyEngine
from app.services.serpapi.orchestrator import (
    SearchOrchestrator,
    EngineExecutionReport,
    OrchestrationResult,
)
from app.services.serpapi.jobs import JobsEngineResult, JobResultItem
from app.services.serpapi.search import SearchEngineResult, OrganicResultItem
from app.services.serpapi.trends import TrendsEngineResult, TrendResultItem


def test_extract_technology_topic():
    engine = TechnologyEngine()
    assert engine.extract_technology_topic("Is AI agent development worth learning in 2026?") == "AI Agent Development"
    assert engine.extract_technology_topic("Should I learn LLMs?") == "Large Language Models (LLMs)"
    assert engine.extract_technology_topic("Is PyTorch still the best framework?") == "PyTorch"


def test_build_technology_search_plan():
    engine = TechnologyEngine()
    plan = engine.build_search_plan("AI Agent Development")
    assert len(plan) == 4
    engines = {i.engine for i in plan}
    assert "google_jobs" in engines
    assert "google_trends" in engines
    assert "google_news" in engines
    assert "google_search" in engines


@pytest.mark.asyncio
async def test_technology_analysis_viability_and_recommendation():
    mock_orchestrator = SearchOrchestrator()

    async def mock_execute_plan(instructions):
        reports = []
        for inst in instructions:
            if inst.engine == "google_jobs":
                output = JobsEngineResult(
                    query=inst.query,
                    results=[
                        JobResultItem(title="AI Agent Engineer", company_name="Cognitive Labs", location="Bengaluru"),
                        JobResultItem(title="Multi-Agent Systems Developer", company_name="Hyperscale AI", location="Remote"),
                    ]
                )
                reports.append(EngineExecutionReport(engine="google_jobs", query=inst.query, status="completed", result_count=2, output=output))
            elif inst.engine == "google_trends":
                output = TrendsEngineResult(
                    query=inst.query,
                    results=[TrendResultItem(query=inst.query, average_interest=88.0)]
                )
                reports.append(EngineExecutionReport(engine="google_trends", query=inst.query, status="completed", result_count=1, output=output))
            else:
                output = SearchEngineResult(
                    query=inst.query,
                    results=[
                        OrganicResultItem(title="AI Agents in Enterprise Workflows 2026", snippet="High demand for autonomous agent developers and tool-use architectures."),
                    ]
                )
                reports.append(EngineExecutionReport(engine=inst.engine, query=inst.query, status="completed", result_count=1, output=output))

        return OrchestrationResult(
            total_requested=len(instructions),
            total_successful=len(reports),
            total_failed=0,
            reports=reports,
        )

    mock_orchestrator.execute_plan = AsyncMock(side_effect=mock_execute_plan)
    engine = TechnologyEngine(orchestrator=mock_orchestrator)

    res = await engine.analyze(
        question="Is AI agent development worth learning for a software engineering student in 2026?",
    )

    assert res.mode == "technology"
    assert len(res.technologies) == 1
    tech = res.technologies[0]
    assert tech.technology == "AI Agent Development"
    assert tech.overall_score >= 50.0
    assert tech.verdict in ("STRONGLY WORTH LEARNING", "WORTH LEARNING", "PROCEED WITH CAUTION")
    assert tech.confidence >= 60.0

    # Recommendation checks
    rec = res.recommendation
    assert rec["top_technology"] == "AI Agent Development"
    assert rec["verdict"] == tech.verdict
    assert len(rec["reasons"]) >= 2
    assert len(rec["actions"]) >= 2
