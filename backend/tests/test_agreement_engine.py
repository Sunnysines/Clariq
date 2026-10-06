"""Unit tests for Evidence Agreement and Confidence Engine."""
from datetime import datetime, timezone
import pytest

from app.schemas.evidence import NormalizedEvidence
from app.services.agreement_engine import AgreementEngine


def test_multi_channel_high_confidence():
    now = datetime.now(timezone.utc)
    ev_jobs = NormalizedEvidence(
        id="e-j",
        analysis_id="an-1",
        source_type="job",
        source="LinkedIn",
        url="https://linkedin.com/jobs/1",
        evidence_strength=92.0,
        freshness_score=95.0,
    )
    ev_news = NormalizedEvidence(
        id="e-n",
        analysis_id="an-1",
        source_type="news",
        source="Reuters",
        url="https://reuters.com/article/1",
        evidence_strength=90.0,
        freshness_score=95.0,
    )
    ev_web = NormalizedEvidence(
        id="e-w",
        analysis_id="an-1",
        source_type="web",
        source="TechCrunch",
        url="https://techcrunch.com/article/2",
        evidence_strength=88.0,
        freshness_score=90.0,
    )
    ev_trend = NormalizedEvidence(
        id="e-t",
        analysis_id="an-1",
        source_type="trend",
        source="Google Trends",
        evidence_strength=85.0,
        freshness_score=100.0,
    )

    conf = AgreementEngine.calculate_confidence([ev_jobs, ev_news, ev_web, ev_trend])
    assert conf.score >= 80.0
    assert conf.level == "HIGH"
    assert len(conf.channels_detected) == 4
    assert any("distinct evidence channels" in r for r in conf.reasons)
    assert "e-j" in conf.evidence_ids
    assert "e-t" in conf.evidence_ids


def test_single_channel_lower_confidence():
    # Only single channel with single source
    ev1 = NormalizedEvidence(
        id="e1",
        analysis_id="an-1",
        source_type="job",
        source="Naukri",
        url="https://naukri.com/job/1",
        evidence_strength=75.0,
        freshness_score=50.0,
    )

    conf = AgreementEngine.calculate_confidence([ev1])
    assert conf.score < 60.0
    assert conf.level in ("MEDIUM", "LOW")
    assert any("Single evidence channel only" in r for r in conf.reasons)


def test_duplicate_domain_does_not_inflate():
    # 5 items, but all from the exact same blog domain
    items = [
        NormalizedEvidence(
            id=f"e-{i}",
            analysis_id="an-1",
            source_type="web",
            source="SingleBlog",
            url="https://singleblog.com/post",
            evidence_strength=70.0,
        )
        for i in range(5)
    ]

    conf = AgreementEngine.calculate_confidence(items)
    # Distinct sources count should be 1
    assert conf.distinct_sources_count == 1
    assert any("Limited source diversity" in r for r in conf.reasons)


def test_contradiction_damps_confidence():
    ev_jobs = NormalizedEvidence(
        id="e-j",
        analysis_id="an-1",
        source_type="job",
        source="LinkedIn",
        url="https://linkedin.com/jobs/1",
        evidence_strength=90.0,
        freshness_score=95.0,
    )
    ev_news = NormalizedEvidence(
        id="e-n",
        analysis_id="an-1",
        source_type="news",
        source="Livemint",
        url="https://livemint.com/news/1",
        evidence_strength=85.0,
        freshness_score=90.0,
    )

    conf_clean = AgreementEngine.calculate_confidence([ev_jobs, ev_news], has_contradictions=False)
    conf_conflict = AgreementEngine.calculate_confidence([ev_jobs, ev_news], has_contradictions=True)

    assert conf_conflict.score < conf_clean.score
    assert any("dampened" in r.lower() for r in conf_conflict.reasons)
