"""SerpApi multi-engine package."""
from app.services.serpapi.client import (
    SerpApiClient,
    SerpApiError,
    SerpApiAuthError,
    SerpApiTimeoutError,
    SerpApiRateLimitError,
)
from app.services.serpapi.search import GoogleSearchService, SearchEngineResult, OrganicResultItem
from app.services.serpapi.jobs import GoogleJobsService, JobsEngineResult, JobResultItem
from app.services.serpapi.news import GoogleNewsService, NewsEngineResult, NewsResultItem
from app.services.serpapi.trends import GoogleTrendsService, TrendsEngineResult, TrendResultItem
from app.services.serpapi.local import GoogleLocalService, LocalEngineResult, LocalResultItem
from app.services.serpapi.orchestrator import (
    SearchOrchestrator,
    EngineSearchInstruction,
    EngineExecutionReport,
    OrchestrationResult,
)

__all__ = [
    "SerpApiClient",
    "SerpApiError",
    "SerpApiAuthError",
    "SerpApiTimeoutError",
    "SerpApiRateLimitError",
    "GoogleSearchService",
    "SearchEngineResult",
    "OrganicResultItem",
    "GoogleJobsService",
    "JobsEngineResult",
    "JobResultItem",
    "GoogleNewsService",
    "NewsEngineResult",
    "NewsResultItem",
    "GoogleTrendsService",
    "TrendsEngineResult",
    "TrendResultItem",
    "GoogleLocalService",
    "LocalEngineResult",
    "LocalResultItem",
    "SearchOrchestrator",
    "EngineSearchInstruction",
    "EngineExecutionReport",
    "OrchestrationResult",
]
