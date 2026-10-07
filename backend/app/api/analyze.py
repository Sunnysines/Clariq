"""Analysis API endpoints and orchestration pipeline."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db, async_session_factory
from app.models.models import Analysis, Evidence, Entity, Signal, Contradiction, Search
from app.schemas.schemas import (
    AnalyzeRequest,
    AnalyzeStartResponse,
    AnalysisStatus,
    EvidenceListResponse,
    EvidenceItem,
    EntityListResponse,
    EntityItem,
    SignalListResponse,
    SignalItem,
)
from app.services.career_engine import CareerEngine
from app.services.company_engine import CompanyEngine
from app.services.technology_engine import TechnologyEngine
from app.services.serpapi.orchestrator import SearchOrchestrator

logger = logging.getLogger("clariq.api.analyze")
router = APIRouter(prefix="/api/analyze", tags=["Analysis"])


async def run_analysis_pipeline(analysis_id: str, question: str) -> None:
    """Background task executing the complete 13-stage decision intelligence pipeline."""
    logger.info(f"Starting analysis background pipeline for {analysis_id}: '{question}'")

    async with async_session_factory() as db:
        try:
            # 1. Update stage: understanding
            stmt = select(Analysis).where(Analysis.id == analysis_id)
            res = await db.execute(stmt)
            analysis_rec = res.scalar_one_or_none()
            if not analysis_rec:
                logger.error(f"Analysis record {analysis_id} not found")
                return

            analysis_rec.current_stage = "understanding"
            analysis_rec.status = "processing"
            await db.commit()

            # Intent classification (career, company, technology)
            q_lower = question.lower()
            if any(w in q_lower for w in ("company", "companies", "startup", "firm", "hiring signals")):
                intent = "company"
            elif any(w in q_lower for w in ("technology", "worth learning", "stack", "framework", "agent development")):
                intent = "technology"
            else:
                intent = "career"

            analysis_rec.intent = intent
            analysis_rec.mode = intent
            await db.commit()

            # Callback for stage progression
            async def update_stage(stage_name: str):
                async with async_session_factory() as stage_db:
                    st_stmt = select(Analysis).where(Analysis.id == analysis_id)
                    st_res = await stage_db.execute(st_stmt)
                    rec = st_res.scalar_one_or_none()
                    if rec:
                        rec.current_stage = stage_name
                        await stage_db.commit()

            if intent == "company":
                company_engine = CompanyEngine()
                result = await company_engine.analyze(
                    question=question,
                    analysis_id=analysis_id,
                    on_stage_update=update_stage,
                )
                top_item = result.companies[0] if result.companies else None
                entities_list = result.companies
                entity_type_label = "company"
                entity_name_key = "company"
            elif intent == "technology":
                technology_engine = TechnologyEngine()
                result = await technology_engine.analyze(
                    question=question,
                    analysis_id=analysis_id,
                    on_stage_update=update_stage,
                )
                top_item = result.technologies[0] if result.technologies else None
                entities_list = result.technologies
                entity_type_label = "technology"
                entity_name_key = "technology"
            else:
                career_engine = CareerEngine()
                result = await career_engine.analyze(
                    question=question,
                    analysis_id=analysis_id,
                    on_stage_update=update_stage,
                )
                top_item = result.cities[0] if result.cities else None
                entities_list = result.cities
                entity_type_label = "city"
                entity_name_key = "city"

            # Store Searches and Evidence records in DB
            for item in entities_list:
                item_name = getattr(item, entity_name_key)
                # Store resolved Entity
                db_entity = Entity(
                    analysis_id=analysis_id,
                    name=item_name,
                    normalized_name=item_name,
                    type=entity_type_label,
                    mention_count=item.evidence_count,
                    evidence_score=item.overall_score,
                )
                db.add(db_entity)

                # Store Signals
                for sig in item.signals:
                    db_sig = Signal(
                        id=sig.id,
                        analysis_id=analysis_id,
                        entity=sig.entity,
                        type=sig.type,
                        direction=sig.direction,
                        strength=sig.strength,
                        evidence_count=sig.evidence_count,
                        description=sig.description,
                        evidence_ids=sig.evidence_ids,
                    )
                    db.add(db_sig)

                # Store Contradictions
                for conflict in item.contradictions:
                    db_conflict = Contradiction(
                        id=conflict.id,
                        analysis_id=analysis_id,
                        entity_name=conflict.entity_name,
                        positive_signal=conflict.positive_signal,
                        negative_signal=conflict.negative_signal,
                        severity=conflict.severity,
                        confidence=conflict.confidence,
                        description=conflict.description,
                        evidence_ids=conflict.evidence_ids,
                    )
                    db.add(db_conflict)

            # Re-fetch analysis to update final status and results
            res = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis_rec = res.scalar_one_or_none()
            if analysis_rec and top_item:
                analysis_rec.status = "completed"
                analysis_rec.current_stage = "completed"
                analysis_rec.overall_score = top_item.overall_score
                analysis_rec.confidence_score = top_item.confidence
                analysis_rec.confidence_level = top_item.confidence_level
                analysis_rec.result_data = result.model_dump()
                analysis_rec.completed_at = datetime.now(timezone.utc)
                await db.commit()

            logger.info(f"Analysis {analysis_id} completed successfully.")

        except Exception as exc:
            logger.error(f"Analysis {analysis_id} pipeline failed: {exc}", exc_info=True)
            res = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis_rec = res.scalar_one_or_none()
            if analysis_rec:
                analysis_rec.status = "failed"
                analysis_rec.error_message = str(exc)
                analysis_rec.completed_at = datetime.now(timezone.utc)
                await db.commit()


@router.post("", response_model=AnalyzeStartResponse)
async def start_analysis(
    req: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeStartResponse:
    """Start an evidence-backed decision analysis immediately returning an ID."""
    logger.info(f"Received analysis question: '{req.question}'")

    analysis = Analysis(
        question=req.question.strip(),
        status="processing",
        current_stage="understanding",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    background_tasks.add_task(run_analysis_pipeline, analysis.id, analysis.question)

    return AnalyzeStartResponse(analysis_id=analysis.id, status="processing")


@router.get("/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> AnalysisStatus:
    """Get the current progress, status, and computed results of an analysis."""
    stmt = select(Analysis).where(Analysis.id == analysis_id)
    res = await db.execute(stmt)
    analysis = res.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return AnalysisStatus(
        id=analysis.id,
        question=analysis.question,
        intent=analysis.intent,
        mode=analysis.mode,
        status=analysis.status,
        current_stage=analysis.current_stage,
        overall_score=analysis.overall_score,
        confidence_score=analysis.confidence_score,
        confidence_level=analysis.confidence_level,
        result_data=analysis.result_data,
        error_message=analysis.error_message,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )


@router.get("/{analysis_id}/evidence", response_model=EvidenceListResponse)
async def get_analysis_evidence(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> EvidenceListResponse:
    """Retrieve all normalized and evaluated evidence records for an analysis."""
    stmt = select(Evidence).where(Evidence.analysis_id == analysis_id)
    res = await db.execute(stmt)
    items = res.scalars().all()

    evidence_items = [
        EvidenceItem(
            id=e.id,
            analysis_id=e.analysis_id,
            search_id=e.search_id,
            title=e.title,
            url=e.url,
            source=e.source,
            source_type=e.source_type,
            snippet=e.snippet,
            entity=e.entity,
            location=e.location,
            published_at=e.published_at,
            relevance_score=e.relevance_score,
            freshness_score=e.freshness_score,
            reliability_score=e.reliability_score,
            evidence_strength=e.evidence_strength,
        )
        for e in items
    ]

    return EvidenceListResponse(
        analysis_id=analysis_id,
        total=len(evidence_items),
        items=evidence_items,
    )


@router.get("/{analysis_id}/signals", response_model=SignalListResponse)
async def get_analysis_signals(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> SignalListResponse:
    """Retrieve all interpretable decision signals derived from evidence."""
    stmt = select(Signal).where(Signal.analysis_id == analysis_id)
    res = await db.execute(stmt)
    signals = res.scalars().all()

    items = [
        SignalItem(
            id=s.id,
            analysis_id=s.analysis_id,
            entity=s.entity,
            type=s.type,
            direction=s.direction,
            strength=s.strength,
            evidence_count=s.evidence_count,
            description=s.description,
            evidence_ids=s.evidence_ids,
        )
        for s in signals
    ]

    return SignalListResponse(
        analysis_id=analysis_id,
        total=len(items),
        items=items,
    )


@router.get("/{analysis_id}/entities", response_model=EntityListResponse)
async def get_analysis_entities(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
) -> EntityListResponse:
    """Retrieve resolved entities for an analysis."""
    stmt = select(Entity).where(Entity.analysis_id == analysis_id)
    res = await db.execute(stmt)
    entities = res.scalars().all()

    items = [
        EntityItem(
            id=ent.id,
            analysis_id=ent.analysis_id,
            name=ent.name,
            normalized_name=ent.normalized_name,
            type=ent.type,
            mention_count=ent.mention_count,
            evidence_score=ent.evidence_score,
        )
        for ent in entities
    ]

    return EntityListResponse(
        analysis_id=analysis_id,
        total=len(items),
        items=items,
    )
