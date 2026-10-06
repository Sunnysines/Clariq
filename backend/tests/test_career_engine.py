"""Unit tests for Career Intelligence Decision Engine."""
from unittest.mock import AsyncMock
import pytest

from app.services.career_engine import CareerEngine
from app.services.serpapi.orchestrator import (
    SearchOrchestrator,
    EngineExecutionReport,
    OrchestrationResult,
)
from app.services.serpapi.jobs import JobsEngineResult, JobResultItem
from app.services.serpapi.search import SearchEngineResult, OrganicResultItem
from app.services.serpapi.trends import TrendsEngineResult, TrendResultItem


def test_build_search_plan():
    engine = CareerEngine()
    cities = ["Bengaluru", "Hyderabad"]
    plan = engine.build_search_plan("Best city for AI in 2026?", cities)

    # 1 trends query + (4 engines * 2 cities) = 9 instructions
    assert len(plan) == 9
    engines_present = {i.engine for i in plan}
    assert "google_trends" in engines_present
    assert "google_jobs" in engines_present
    assert "google_search" in engines_present
    assert "google_news" in engines_present
    assert "google_local" in engines_present


@pytest.mark.asyncio
async def test_career_analysis_ranking_and_explanation():
    # Mock search orchestrator to return simulated SerpApi outputs for Bengaluru and Hyderabad
    mock_orchestrator = SearchOrchestrator()

    async def mock_execute_plan(instructions):
        reports = []
        for inst in instructions:
            if inst.engine == "google_jobs" and "Bengaluru" in inst.query:
                # Bengaluru gets more open jobs
                output = JobsEngineResult(
                    query=inst.query,
                    results=[
                        JobResultItem(title="AI Engineer", company_name="Google", location="Bengaluru"),
                        JobResultItem(title="ML Researcher", company_name="Microsoft", location="Bengaluru"),
                        JobResultItem(title="Deep Learning Specialist", company_name="Infosys", location="Bengaluru"),
                    ]
                )
                reports.append(EngineExecutionReport(engine="google_jobs", query=inst.query, status="completed", result_count=3, output=output))
            elif inst.engine == "google_jobs" and "Hyderabad" in inst.query:
                # Hyderabad gets 1 job
                output = JobsEngineResult(
                    query=inst.query,
                    results=[
                        JobResultItem(title="Data Scientist", company_name="Amazon", location="Hyderabad"),
                    ]
                )
                reports.append(EngineExecutionReport(engine="google_jobs", query=inst.query, status="completed", result_count=1, output=output))
            elif inst.engine == "google_trends":
                output = TrendsEngineResult(
                    query="AI engineer jobs",
                    results=[TrendResultItem(query="AI engineer jobs", average_interest=85.0)]
                )
                reports.append(EngineExecutionReport(engine="google_trends", query=inst.query, status="completed", result_count=1, output=output))
            else:
                # General search or news
                output = SearchEngineResult(
                    query=inst.query,
                    results=[OrganicResultItem(title=f"AI Tech Ecosystem in {inst.location or 'India'}", snippet=f"Strong growth and startups in {inst.location or 'India'}.")]
                )
                reports.append(EngineExecutionReport(engine=inst.engine, query=inst.query, status="completed", result_count=1, output=output))

        return OrchestrationResult(
            total_requested=len(instructions),
            total_successful=len(reports),
            total_failed=0,
            reports=reports,
        )

    mock_orchestrator.execute_plan = AsyncMock(side_effect=mock_execute_plan)
    career_engine = CareerEngine(orchestrator=mock_orchestrator)

    res = await career_engine.analyze(
        question="Which Indian city is best for an entry-level AI/ML career in 2026?",
        target_cities=["Bengaluru", "Hyderabad"],
    )

    # 1. Output structure
    assert res.mode == "career"
    assert len(res.cities) == 2
    assert res.top_city in ("Bengaluru", "Hyderabad")

    # 2. Ranking check: Top city must have highest overall score
    assert res.cities[0].overall_score >= res.cities[1].overall_score
    assert res.cities[0].rank == 1
    assert res.cities[1].rank == 2

    # 3. Category scores present
    blr = next(c for c in res.cities if c.city == "Bengaluru")
    assert blr.category_scores.job_opportunity > 0
    assert blr.category_scores.market_demand > 0
    assert blr.category_scores.company_presence > 0

    # 4. Explanation contributions
    contributions = res.explanation["contributions"]
    assert len(contributions) >= 2
    assert any("job" in c["label"].lower() for c in contributions)
    assert res.recommendation["top_city"] == res.top_city
