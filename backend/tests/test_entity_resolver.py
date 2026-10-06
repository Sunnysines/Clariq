"""Unit tests for Entity Resolution & Aggregation Engine."""
import pytest
from app.schemas.evidence import NormalizedEvidence
from app.services.entity_resolver import EntityResolver


def test_city_aliases():
    assert EntityResolver.normalize_city("Bangalore") == "Bengaluru"
    assert EntityResolver.normalize_city("Bengaluru") == "Bengaluru"
    assert EntityResolver.normalize_city("blr") == "Bengaluru"
    assert EntityResolver.normalize_city("Bengaluru, Karnataka") == "Bengaluru"
    assert EntityResolver.normalize_city("Bombay") == "Mumbai"
    assert EntityResolver.normalize_city("Madras") == "Chennai"
    assert EntityResolver.normalize_city("Poona") == "Pune"
    assert EntityResolver.normalize_city("Gurgaon") == "Gurugram"


def test_company_legal_names_and_aliases():
    assert EntityResolver.normalize_company("Microsoft") == "Microsoft"
    assert EntityResolver.normalize_company("Microsoft India") == "Microsoft"
    assert EntityResolver.normalize_company("Microsoft Corporation") == "Microsoft"
    assert EntityResolver.normalize_company("Microsoft India Pvt Ltd") == "Microsoft"
    assert EntityResolver.normalize_company("Microsoft India Private Limited") == "Microsoft"
    assert EntityResolver.normalize_company("Google LLC") == "Google"
    assert EntityResolver.normalize_company("Amazon Web Services") == "Amazon"
    assert EntityResolver.normalize_company("Tata Consultancy Services") == "TCS"
    assert EntityResolver.normalize_company("Infosys Technologies Ltd") == "Infosys"


def test_capitalization_handling():
    assert EntityResolver.normalize_company("mIcRoSoFt") == "Microsoft"
    assert EntityResolver.normalize_city("bEnGaLuRu") == "Bengaluru"
    assert EntityResolver.normalize_technology("pytorch") == "PyTorch"
    assert EntityResolver.normalize_technology("genai") == "Generative AI"


def test_prevent_false_matches():
    # MicroStrategy should NOT be resolved to Microsoft
    assert EntityResolver.normalize_company("MicroStrategy") != "Microsoft"
    assert EntityResolver.normalize_company("MicroStrategy") == "Microstrategy"

    # Distinct cities must not collide
    assert EntityResolver.normalize_city("Pune") != "Chennai"
    assert EntityResolver.normalize_city("Hyderabad") != "Bengaluru"


def test_technology_aliases():
    assert EntityResolver.normalize_technology("AI & ML") == "AI/ML"
    assert EntityResolver.normalize_technology("Artificial Intelligence and Machine Learning") == "AI/ML"
    assert EntityResolver.normalize_technology("LLMs") == "LLMs"
    assert EntityResolver.normalize_technology("Large Language Models") == "LLMs"


def test_evidence_aggregation_by_entity():
    ev1 = NormalizedEvidence(
        id="e1",
        analysis_id="an-1",
        source_type="job",
        title="AI Engineer",
        entity="Microsoft",
        location="Bengaluru",
        evidence_strength=90.0,
    )
    ev2 = NormalizedEvidence(
        id="e2",
        analysis_id="an-1",
        source_type="news",
        title="Microsoft announces new AI R&D hub",
        entity="Microsoft India Pvt Ltd",
        location="Bengaluru",
        evidence_strength=85.0,
    )
    ev3 = NormalizedEvidence(
        id="e3",
        analysis_id="an-1",
        source_type="job",
        title="ML Engineer in Hyderabad",
        entity="Google",
        location="Hyderabad",
        evidence_strength=80.0,
    )

    resolved_cities = EntityResolver.aggregate_evidence_by_entity(
        [ev1, ev2, ev3],
        analysis_id="an-1",
        entity_type="city",
        target_entities=["Bengaluru", "Hyderabad", "Pune"]
    )

    blr = next(c for c in resolved_cities if c.normalized_name == "Bengaluru")
    assert blr.mention_count == 2
    assert blr.by_source_type["job"] == 1
    assert blr.by_source_type["news"] == 1
    assert len(blr.evidence_ids) == 2

    hyd = next(c for c in resolved_cities if c.normalized_name == "Hyderabad")
    assert hyd.mention_count == 1
    assert hyd.by_source_type["job"] == 1
