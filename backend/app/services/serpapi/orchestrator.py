"""SearchOrchestrator – coordinates multi-engine SerpApi queries with graceful partial failure tolerance."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional, Union
from pydantic import BaseModel, Field

from app.services.serpapi.client import SerpApiClient
from app.services.serpapi.search import GoogleSearchService, SearchEngineResult
from app.services.serpapi.jobs import GoogleJobsService, JobsEngineResult
from app.services.serpapi.news import GoogleNewsService, NewsEngineResult
from app.services.serpapi.trends import GoogleTrendsService, TrendsEngineResult
from app.services.serpapi.local import GoogleLocalService, LocalEngineResult

logger = logging.getLogger("clariq.orchestrator")

EngineOutput = Union[SearchEngineResult, JobsEngineResult, NewsEngineResult, TrendsEngineResult, LocalEngineResult]


class EngineSearchInstruction(BaseModel):
    engine: str  # google_search | google_jobs | google_news | google_trends | google_local
    query: str
    location: Optional[str] = None
    geo: Optional[str] = None
    num: Optional[int] = 10


class EngineExecutionReport(BaseModel):
    engine: str
    query: str
    status: str  # completed | failed
    result_count: int = 0
    error_message: Optional[str] = None
    output: Optional[EngineOutput] = None


class OrchestrationResult(BaseModel):
    total_requested: int
    total_successful: int
    total_failed: int
    reports: list[EngineExecutionReport] = Field(default_factory=list)

    @property
    def successful_outputs(self) -> list[EngineOutput]:
        return [r.output for r in self.reports if r.status == "completed" and r.output is not None]


class SearchOrchestrator:
    """Orchestrates multi-engine searches across SerpApi with failure resilience."""

    def __init__(self, client: Optional[SerpApiClient] = None):
        self.client = client or SerpApiClient()
        self.search_service = GoogleSearchService(self.client)
        self.jobs_service = GoogleJobsService(self.client)
        self.news_service = GoogleNewsService(self.client)
        self.trends_service = GoogleTrendsService(self.client)
        self.local_service = GoogleLocalService(self.client)

    async def _execute_single(self, instruction: EngineSearchInstruction) -> EngineExecutionReport:
        engine = instruction.engine.lower().strip()
        query = instruction.query.strip()
        logger.info(f"Orchestrator starting query on engine '{engine}': '{query}'")

        try:
            if engine in ("google_search", "search", "google"):
                res = await self.search_service.search(query=query, location=instruction.location, num=instruction.num or 10)
                return EngineExecutionReport(
                    engine="google_search",
                    query=query,
                    status="completed",
                    result_count=len(res.results),
                    output=res,
                )

            elif engine in ("google_jobs", "jobs"):
                res = await self.jobs_service.search(query=query, location=instruction.location)
                return EngineExecutionReport(
                    engine="google_jobs",
                    query=query,
                    status="completed",
                    result_count=len(res.results),
                    output=res,
                )

            elif engine in ("google_news", "news"):
                res = await self.news_service.search(query=query, location=instruction.location)
                return EngineExecutionReport(
                    engine="google_news",
                    query=query,
                    status="completed",
                    result_count=len(res.results),
                    output=res,
                )

            elif engine in ("google_trends", "trends"):
                res = await self.trends_service.search(query=query, geo=instruction.geo or instruction.location)
                return EngineExecutionReport(
                    engine="google_trends",
                    query=query,
                    status="completed",
                    result_count=len(res.results),
                    output=res,
                )

            elif engine in ("google_local", "local", "maps"):
                res = await self.local_service.search(query=query, location=instruction.location)
                return EngineExecutionReport(
                    engine="google_local",
                    query=query,
                    status="completed",
                    result_count=len(res.results),
                    output=res,
                )

            else:
                return EngineExecutionReport(
                    engine=engine,
                    query=query,
                    status="failed",
                    error_message=f"Unsupported SerpApi engine '{engine}'",
                )

        except Exception as exc:
            logger.error(f"Engine '{engine}' failed for query '{query}': {exc}", exc_info=True)
            return EngineExecutionReport(
                engine=engine,
                query=query,
                status="failed",
                error_message=str(exc),
            )

    async def execute_plan(
        self,
        instructions: list[EngineSearchInstruction],
    ) -> OrchestrationResult:
        """Execute multiple search instructions concurrently, continuing gracefully if some fail."""
        if not instructions:
            return OrchestrationResult(total_requested=0, total_successful=0, total_failed=0, reports=[])

        tasks = [self._execute_single(inst) for inst in instructions]
        reports: list[EngineExecutionReport] = await asyncio.gather(*tasks)

        successful = sum(1 for r in reports if r.status == "completed")
        failed = sum(1 for r in reports if r.status == "failed")

        logger.info(
            f"SearchOrchestration completed: {successful}/{len(instructions)} succeeded, {failed} failed."
        )

        return OrchestrationResult(
            total_requested=len(instructions),
            total_successful=successful,
            total_failed=failed,
            reports=reports,
        )
