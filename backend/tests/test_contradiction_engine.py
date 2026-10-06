"""Unit tests for Contradiction Detection Engine."""
import pytest
from app.services.signal_engine import DecisionSignal
from app.services.contradiction_engine import ContradictionEngine


def test_true_contradiction_hiring_vs_risk():
    sig_hiring = DecisionSignal(
        analysis_id="an-1",
        entity="Microsoft",
        type="HIRING",
        direction="positive",
        strength=88.0,
        evidence_count=15,
        description="15 open AI positions detected across engineering centers",
        evidence_ids=["e-h1", "e-h2"],
    )
    sig_risk = DecisionSignal(
        analysis_id="an-1",
        entity="Microsoft",
        type="RISK",
        direction="negative",
        strength=82.0,
        evidence_count=3,
        description="Layoffs reported in selective divisions",
        evidence_ids=["e-r1"],
    )

    summary = ContradictionEngine.detect_conflicts_for_entity([sig_hiring, sig_risk], "Microsoft", "an-1")
    assert summary.has_conflict is True
    assert summary.severity == "high"
    assert len(summary.conflicts) == 1

    conflict = summary.conflicts[0]
    assert "e-h1" in conflict.evidence_ids
    assert "e-r1" in conflict.evidence_ids
    assert conflict.confidence == 85.0


def test_unrelated_evidence_no_contradiction():
    # POPULARITY and INVESTMENT are both positive, no opposing negative signal
    sig_pop = DecisionSignal(
        analysis_id="an-1",
        entity="Bengaluru",
        type="POPULARITY",
        direction="positive",
        strength=80.0,
        evidence_count=1,
        description="High search demand for ML careers",
        evidence_ids=["e-p1"],
    )
    sig_inv = DecisionSignal(
        analysis_id="an-1",
        entity="Bengaluru",
        type="INVESTMENT",
        direction="positive",
        strength=85.0,
        evidence_count=2,
        description="New AI R&D hub announced",
        evidence_ids=["e-i1"],
    )

    summary = ContradictionEngine.detect_conflicts_for_entity([sig_pop, sig_inv], "Bengaluru", "an-1")
    assert summary.has_conflict is False
    assert summary.severity is None
    assert len(summary.conflicts) == 0


def test_weak_conflict_severity():
    sig_hiring = DecisionSignal(
        analysis_id="an-1",
        entity="StartupZ",
        type="HIRING",
        direction="positive",
        strength=45.0,  # weak
        evidence_count=1,
        description="1 potential opening",
        evidence_ids=["e-1"],
    )
    sig_risk = DecisionSignal(
        analysis_id="an-1",
        entity="StartupZ",
        type="RISK",
        direction="negative",
        strength=40.0,  # weak
        evidence_count=1,
        description="Unverified slowdown rumour",
        evidence_ids=["e-2"],
    )

    summary = ContradictionEngine.detect_conflicts_for_entity([sig_hiring, sig_risk], "StartupZ", "an-1")
    assert summary.has_conflict is True
    assert summary.severity == "low"


def test_multiple_conflicts():
    sig_hiring = DecisionSignal(
        analysis_id="an-1",
        entity="CompanyA",
        type="HIRING",
        direction="positive",
        strength=80.0,
        evidence_count=5,
        description="Hiring aggressively in Bangalore",
        evidence_ids=["e-h"],
    )
    sig_growth = DecisionSignal(
        analysis_id="an-1",
        entity="CompanyA",
        type="GROWTH",
        direction="positive",
        strength=75.0,
        evidence_count=3,
        description="Expanding office footprint",
        evidence_ids=["e-g"],
    )
    sig_risk = DecisionSignal(
        analysis_id="an-1",
        entity="CompanyA",
        type="RISK",
        direction="negative",
        strength=85.0,
        evidence_count=4,
        description="Hiring freeze across non-core teams",
        evidence_ids=["e-r"],
    )

    summary = ContradictionEngine.detect_conflicts_for_entity([sig_hiring, sig_growth, sig_risk], "CompanyA", "an-1")
    assert summary.has_conflict is True
    # Contradicts both HIRING and GROWTH
    assert len(summary.conflicts) == 2
