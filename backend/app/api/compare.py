"""Entity Comparison API router."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db, async_session_factory
from app.models.models import Analysis
from app.schemas.schemas import CompareRequest, AnalyzeStartResponse
from app.api.analyze import run_analysis_pipeline

logger = logging.getLogger("clariq.api.compare")
router = APIRouter(prefix="/api/compare", tags=["Compare"])


@router.post("", response_model=AnalyzeStartResponse)
async def start_entity_comparison(
    req: CompareRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeStartResponse:
    """Start an entity comparison reusing the core decision intelligence engine."""
    logger.info(f"Starting comparison analysis: '{req.question}' for entities {req.entities}")

    analysis = Analysis(
        question=req.question.strip(),
        intent=req.mode or "career",
        mode="compare",
        status="processing",
        current_stage="understanding",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    background_tasks.add_task(run_analysis_pipeline, analysis.id, analysis.question)

    return AnalyzeStartResponse(analysis_id=analysis.id, status="processing")
