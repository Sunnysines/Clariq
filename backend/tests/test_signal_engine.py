"""Unit tests for Evidence-Driven Signal Engine."""
from datetime import datetime, timezone
import pytest

from app.schemas.evidence import NormalizedEvidence
from app.services.signal_engine import SignalEngine


def test_hiring_signal_derivation():
    ev1 = NormalizedEvidence(
        id="e-job-1",
        analysis_id="an-1",
        source_type="job",
        title="Senior AI Researcher",
        evidence_strength=88.0,
    )
    ev2 = NormalizedEvidence(
        id="e-job-2",
        analysis_id="an-1",
        source_type="job",
        title="ML Operations Engineer",
        evidence_strength=90.0,
    )

    signals = SignalEngine.extract_signals_for_entity([ev1, ev2], entity_name="Bengaluru", analysis_id="an-1")
    hiring_sig = next((s for s in signals if s.type == "HIRING"), None)

    assert hiring_sig is not None
    assert hiring_sig.direction == "positive"
    assert hiring_sig.evidence_count == 2
    assert "e-job-1" in hiring_sig.evidence_ids
    assert "e-job-2" in hiring_sig.evidence_ids
    assert hiring_sig.strength >= 88.0


def test_risk_signal_derivation():
    ev_risk = NormalizedEvidence(
        id="e-risk-1",
        analysis_id="an-1",
        source_type="news",
        title="Tech conglomerate announces selective hiring freeze and restructuring",
        snippet="Cost-cutting initiative includes workforce reduction across redundant units.",
        evidence_strength=82.0,
    )

    signals = SignalEngine.extract_signals_for_entity([ev_risk], entity_name="EntityX", analysis_id="an-1")
    risk_sig = next((s for s in signals if s.type == "RISK"), None)

    assert risk_sig is not None
    assert risk_sig.direction == "negative"
    assert "e-risk-1" in risk_sig.evidence_ids
    assert "workforce adjustments" in risk_sig.description


def test_investment_and_popularity_signals():
    ev_inv = NormalizedEvidence(
        id="e-inv-1",
        analysis_id="an-1",
        source_type="news",
        title="AI startup raises $50M Series B for Bengaluru expansion",
        snippet="Venture capital infusion to build new research facility.",
        evidence_strength=86.0,
    )
    ev_trend = NormalizedEvidence(
        id="e-trend-1",
        analysis_id="an-1",
        source_type="trend",
        title="Google Trends: AI Engineer Jobs",
        snippet="Average relative interest index: 88/100",
        evidence_strength=85.0,
    )

    signals = SignalEngine.extract_signals_for_entity([ev_inv, ev_trend], entity_name="Bengaluru", analysis_id="an-1")
    types = {s.type for s in signals}
    assert "INVESTMENT" in types
    assert "POPULARITY" in types


def test_no_unsupported_signals_invented():
    # Only unrelated text
    ev_neutral = NormalizedEvidence(
        id="e-neutral-1",
        analysis_id="an-1",
        source_type="web",
        title="General weather report for Bengaluru",
        snippet="Partly cloudy today with mild afternoon temperatures.",
        evidence_strength=60.0,
        freshness_score=50.0,
    )

    signals = SignalEngine.extract_signals_for_entity([ev_neutral], entity_name="Bengaluru", analysis_id="an-1")
    # Must not fabricate HIRING, RISK, or INVESTMENT without evidence
    types = {s.type for s in signals}
    assert "HIRING" not in types
    assert "RISK" not in types
    assert "INVESTMENT" not in types
