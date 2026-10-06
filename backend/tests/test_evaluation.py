"""Unit tests for evidence evaluation (freshness, relevance, reliability, strength)."""
from datetime import datetime, timezone, timedelta
import pytest

from app.schemas.evidence import NormalizedEvidence
from app.services.freshness_engine import FreshnessEngine
from app.services.relevance_engine import RelevanceEngine, ReliabilityScorer


def test_freshness_scoring_tiers():
    now = datetime.now(timezone.utc)

    # Today <= 1 day
    assert FreshnessEngine.calculate_score(now - timedelta(hours=6)) == 100.0

    # 1-3 days
    assert FreshnessEngine.calculate_score(now - timedelta(days=2)) == 95.0

    # 4-7 days
    assert FreshnessEngine.calculate_score(now - timedelta(days=5)) == 90.0

    # 8-30 days
    assert FreshnessEngine.calculate_score(now - timedelta(days=20)) == 75.0

    # 31-90 days
    assert FreshnessEngine.calculate_score(now - timedelta(days=60)) == 50.0

    # > 90 days
    assert FreshnessEngine.calculate_score(now - timedelta(days=120)) == 25.0

    # Unknown date
    assert FreshnessEngine.calculate_score(None) == 40.0


def test_source_reliability_assumptions():
    # Google jobs / linkedin
    assert ReliabilityScorer.calculate_reliability("LinkedIn", "job", "https://linkedin.com/jobs/1") == 90.0

    # Major news
    assert ReliabilityScorer.calculate_reliability("Reuters", "news", "https://reuters.com/tech/1") == 90.0

    # Official company careers
    assert ReliabilityScorer.calculate_reliability("Microsoft", "web", "https://careers.microsoft.com/us") == 95.0

    # Forum
    assert ReliabilityScorer.calculate_reliability("Reddit", "web", "https://reddit.com/r/cscareerquestions") == 50.0

    # General web
    assert ReliabilityScorer.calculate_reliability("SomeBlog", "web", "https://randomblog.org/tips") == 70.0


def test_high_vs_low_relevance():
    query = "AI ML entry level jobs in Bengaluru"

    high_ev = NormalizedEvidence(
        analysis_id="an-1",
        source_type="job",
        title="Entry-Level Machine Learning Engineer, Bengaluru",
        snippet="Hiring junior AI engineer in Bengaluru. Experience with Python, PyTorch, salary competitive.",
        location="Bengaluru, Karnataka",
        source="Google Jobs",
        url="https://linkedin.com/jobs/ai-blr",
        published_at=datetime.now(timezone.utc),
    )

    low_ev = NormalizedEvidence(
        analysis_id="an-1",
        source_type="web",
        title="Best tourist places to visit in Goa",
        snippet="Beaches, restaurants, and nightlife guide for holiday travelers.",
        location="Goa",
        source="TravelGuide",
        url="https://travelguide.com/goa",
        published_at=datetime.now(timezone.utc) - timedelta(days=100),
    )

    scored_high = RelevanceEngine.evaluate(high_ev, query=query, target_location="Bengaluru", intent="career")
    scored_low = RelevanceEngine.evaluate(low_ev, query=query, target_location="Bengaluru", intent="career")

    assert scored_high.relevance_score is not None
    assert scored_low.relevance_score is not None
    assert scored_high.relevance_score > 75.0
    assert scored_low.relevance_score < 40.0
    assert scored_high.evidence_strength > scored_low.evidence_strength


def test_evidence_strength_formula():
    ev = NormalizedEvidence(
        analysis_id="an-1",
        source_type="job",
        title="AI Engineer",
        url="https://naukri.com/job/1",
        published_at=datetime.now(timezone.utc) - timedelta(days=2),  # freshness = 95
    )

    # Mock specific scores
    ev = RelevanceEngine.evaluate(ev, query="AI Engineer", intent="career")

    expected_strength = round(
        (0.5 * ev.relevance_score) + (0.3 * ev.freshness_score) + (0.2 * ev.reliability_score),
        1
    )
    assert ev.evidence_strength == expected_strength
