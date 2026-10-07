"""Unit tests for Company Intelligence Decision Engine."""
from unittest.mock import AsyncMock
import pytest

from app.services.company_engine import CompanyEngine
from app.services.serpapi.orchestrator import (
    SearchOrchestrator,
    EngineExecutionReport,
    OrchestrationResult,
)
from app.services.serpapi.jobs import JobsEngineResult, JobResultItem
from app.services.serpapi.news import NewsEngineResult, NewsResultItem
from app.services.serpapi.search import SearchEngineResult, OrganicResultItem


def test_build_company_search_plan():
    engine = CompanyEngine()
    plan = engine.build_search_plan("Which Indian companies show strong AI hiring signals?")
    assert len(plan) == 6
    engines = {i.engine for i in plan}
    assert "google_jobs" in engines
    assert "google_news" in engines
    assert "google_search" in engines
    assert "google_trends" in engines


@pytest.mark.asyncio
async def test_company_analysis_dynamic_discovery_and_ranking():
    mock_orchestrator = SearchOrchestrator()

    async def mock_execute_plan(instructions):
        reports = []
        for inst in instructions:
            if inst.engine == "google_jobs":
                output = JobsEngineResult(
                    query=inst.query,
                    results=[
                        JobResultItem(title="Senior ML Engineer", company_name="Microsoft India Pvt Ltd", location="Bengaluru"),
                        JobResultItem(title="AI Research Lead", company_name="Microsoft", location="Hyderabad"),
                        JobResultItem(title="AI Associate", company_name="Infosys Technologies Ltd", location="Pune"),
                    ]
                )
                reports.append(EngineExecutionReport(engine="google_jobs", query=inst.query, status="completed", result_count=3, output=output))
            elif inst.engine == "google_news" and "layoffs" in inst.query:
                output = NewsEngineResult(
                    query=inst.query,
                    results=[
                        NewsResultItem(title="Infosys announces cautious hiring review", snippet="Workforce adjustment in non-tech units."),
                    ]
                )
                reports.append(EngineExecutionReport(engine="google_news", query=inst.query, status="completed", result_count=1, output=output))
            else:
                output = SearchEngineResult(
                    query=inst.query,
                    results=[
                        OrganicResultItem(title="Microsoft invests $3B in India AI infrastructure", snippet="Aggressive expansion across India data centers."),
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
    engine = CompanyEngine(orchestrator=mock_orchestrator)

    res = await engine.analyze(
        question="Which Indian companies currently show strong AI hiring signals?",
    )

    assert res.mode == "company"
    assert len(res.companies) >= 2
    # Verify entity normalization worked dynamically (Microsoft India Pvt Ltd -> Microsoft)
    comp_names = [c.company for c in res.companies]
    assert "Microsoft" in comp_names
    assert "Infosys" in comp_names

    # Check ranking
    assert res.companies[0].overall_score >= res.companies[1].overall_score
    assert res.top_company == res.companies[0].company

    # Check signals
    msft = next(c for c in res.companies if c.company == "Microsoft")
    assert msft.hiring_signals_count > 0
    assert msft.evidence_count > 0
