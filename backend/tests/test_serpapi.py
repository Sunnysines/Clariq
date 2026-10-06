"""Unit tests for SerpApi client and engines."""
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.services.serpapi.client import (
    SerpApiClient,
    SerpApiAuthError,
    SerpApiTimeoutError,
    SerpApiError,
)
from app.services.serpapi.search import GoogleSearchService
from app.services.serpapi.jobs import GoogleJobsService
from app.services.serpapi.news import GoogleNewsService
from app.services.serpapi.trends import GoogleTrendsService
from app.services.serpapi.local import GoogleLocalService
from app.services.serpapi.orchestrator import SearchOrchestrator, EngineSearchInstruction


def test_client_configuration():
    client = SerpApiClient(api_key="test_key_123", timeout=10, max_retries=1)
    assert client.api_key == "test_key_123"
    assert client.timeout == 10
    assert client.max_retries == 1


@pytest.mark.asyncio
async def test_missing_or_invalid_api_key():
    client = SerpApiClient(api_key="")
    with pytest.raises(SerpApiAuthError):
        await client.execute({"engine": "google", "q": "test"})


@pytest.mark.asyncio
async def test_timeout_handling():
    client = SerpApiClient(api_key="valid_key", timeout=1, max_retries=0)
    
    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectTimeout("Connection timed out")):
        with pytest.raises(SerpApiTimeoutError):
            await client.execute({"engine": "google", "q": "timeout test"})


@pytest.mark.asyncio
async def test_successful_search_parsing():
    mock_payload = {
        "search_information": {"total_results": 1500000},
        "organic_results": [
            {
                "position": 1,
                "title": "Machine Learning Engineer in Bengaluru",
                "link": "https://example.com/ml-blr",
                "snippet": "Leading AI opportunities in Bengaluru for 2026.",
                "displayed_link": "example.com",
            }
        ]
    }

    client = SerpApiClient(api_key="test_key")
    client.execute = AsyncMock(return_value=mock_payload)
    service = GoogleSearchService(client=client)

    result = await service.search(query="AI ML Bengaluru")
    assert result.engine == "google_search"
    assert len(result.results) == 1
    assert result.results[0].title == "Machine Learning Engineer in Bengaluru"
    assert result.results[0].link == "https://example.com/ml-blr"


@pytest.mark.asyncio
async def test_successful_jobs_parsing():
    mock_payload = {
        "jobs_results": [
            {
                "title": "Associate AI Engineer",
                "company_name": "Clariq Labs",
                "location": "Bengaluru, Karnataka",
                "via": "LinkedIn",
                "description": "Looking for entry level AI engineer",
                "apply_options": [{"link": "https://linkedin.com/jobs/123"}],
                "detected_extensions": {"posted_at": "1 day ago", "schedule_type": "Full-time"},
            }
        ]
    }

    client = SerpApiClient(api_key="test_key")
    client.execute = AsyncMock(return_value=mock_payload)
    service = GoogleJobsService(client=client)

    result = await service.search(query="AI Engineer", location="Bengaluru")
    assert result.engine == "google_jobs"
    assert len(result.results) == 1
    assert result.results[0].company_name == "Clariq Labs"
    assert result.results[0].link == "https://linkedin.com/jobs/123"


@pytest.mark.asyncio
async def test_failed_engine_handling_in_orchestrator():
    client = SerpApiClient(api_key="test_key")

    # Mock execute so that google_news fails, but google_jobs and google_search succeed
    async def mock_execute(params):
        engine = params.get("engine")
        if engine == "google_news":
            raise SerpApiError("SerpApi news engine rate limited", status_code=429)
        elif engine == "google_jobs":
            return {"jobs_results": [{"title": "Data Scientist", "company_name": "Google"}]}
        elif engine == "google":
            return {"organic_results": [{"title": "Tech in Bengaluru", "link": "https://example.com"}]}
        return {}

    client.execute = AsyncMock(side_effect=mock_execute)
    orchestrator = SearchOrchestrator(client=client)

    instructions = [
        EngineSearchInstruction(engine="google_jobs", query="AI engineer", location="Bengaluru"),
        EngineSearchInstruction(engine="google_news", query="AI startups", location="Bengaluru"),
        EngineSearchInstruction(engine="google_search", query="Tech hubs India"),
    ]

    orch_res = await orchestrator.execute_plan(instructions)
    assert orch_res.total_requested == 3
    assert orch_res.total_successful == 2
    assert orch_res.total_failed == 1

    # Verify that the failed engine has error message and the other two completed
    news_report = next(r for r in orch_res.reports if r.engine == "google_news")
    assert news_report.status == "failed"
    assert "rate limited" in news_report.error_message

    jobs_report = next(r for r in orch_res.reports if r.engine == "google_jobs")
    assert jobs_report.status == "completed"
    assert jobs_report.result_count == 1
