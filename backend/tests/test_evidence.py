"""Unit tests for evidence normalization engine."""
import pytest
from app.services.evidence_engine import EvidenceEngine, _parse_relative_date
from app.services.serpapi.search import OrganicResultItem, SearchEngineResult
from app.services.serpapi.jobs import JobResultItem, JobsEngineResult
from app.services.serpapi.news import NewsResultItem, NewsEngineResult
from app.services.serpapi.trends import TrendResultItem, TrendDataPoint, TrendsEngineResult
from app.services.serpapi.local import LocalResultItem, LocalEngineResult
from app.services.serpapi.orchestrator import EngineExecutionReport


def test_date_parser_does_not_fabricate():
    assert _parse_relative_date(None) is None
    assert _parse_relative_date("") is None
    assert _parse_relative_date("invalid-date-string") is None

    # Valid relative strings
    d1 = _parse_relative_date("2 days ago")
    assert d1 is not None

    d2 = _parse_relative_date("5 hours ago")
    assert d2 is not None


def test_normalize_search_item():
    engine = EvidenceEngine()
    item = OrganicResultItem(
        title="Top AI Startups in Bengaluru 2026",
        link="https://techcrunch.com/article/ai-blr",
        snippet="Bengaluru leads Indian tech ecosystem with 40% AI funding share.",
        date="1 day ago",
        source="TechCrunch",
    )

    norm = engine.normalize_search_item(item, analysis_id="test-an-1", location="Bengaluru")
    assert norm.source_type == "web"
    assert norm.title == "Top AI Startups in Bengaluru 2026"
    assert norm.url == "https://techcrunch.com/article/ai-blr"
    assert norm.source == "TechCrunch"
    assert norm.snippet is not None
    assert norm.published_at is not None
    assert norm.raw_engine == "google_search"


def test_normalize_job_item():
    engine = EvidenceEngine()
    item = JobResultItem(
        title="Junior Machine Learning Engineer",
        company_name="Infosys",
        location="Bengaluru, Karnataka",
        via="via LinkedIn",
        description="Requires PyTorch, Python, LLM evaluation skills.",
        link="https://linkedin.com/jobs/view/12345",
        posted_at="3 days ago",
        extensions=["Full-time", "Competitive salary"],
    )

    norm = engine.normalize_job_item(item, analysis_id="test-an-1")
    assert norm.source_type == "job"
    assert "Junior Machine Learning Engineer" in norm.title
    assert norm.entity == "Infosys"
    assert norm.source == "LinkedIn"
    assert norm.url == "https://linkedin.com/jobs/view/12345"
    assert "PyTorch" in norm.snippet
    assert norm.raw_engine == "google_jobs"


def test_normalize_news_item():
    engine = EvidenceEngine()
    item = NewsResultItem(
        title="NVIDIA partners with Indian AI startups in Hyderabad",
        link="https://reuters.com/tech/nvidia-hyd",
        source="Reuters",
        date="Feb 12, 2026",
        snippet="Collaboration focuses on GPU access for computer vision teams.",
    )

    norm = engine.normalize_news_item(item, analysis_id="test-an-1")
    assert norm.source_type == "news"
    assert norm.title == "NVIDIA partners with Indian AI startups in Hyderabad"
    assert norm.source == "Reuters"
    assert norm.raw_engine == "google_news"


def test_normalize_trends_item():
    engine = EvidenceEngine()
    item = TrendResultItem(
        query="AI Engineer Jobs",
        average_interest=84.5,
        timeline_data=[
            TrendDataPoint(date="2026-01-01", value=80),
            TrendDataPoint(date="2026-02-01", value=89),
        ],
    )

    norm = engine.normalize_trends_item(item, analysis_id="test-an-1", geo="IN")
    assert norm.source_type == "trend"
    assert "Search Interest" in norm.title
    assert "84.5/100" in norm.snippet
    assert norm.url is None  # no fabrication of URL


def test_normalize_local_item():
    engine = EvidenceEngine()
    item = LocalResultItem(
        title="Indian Institute of Science AI Lab",
        address="CV Raman Rd, Bengaluru",
        rating=4.9,
        reviews=120,
        type="Research Institute",
        website="https://iisc.ac.in",
    )

    norm = engine.normalize_local_item(item, analysis_id="test-an-1")
    assert norm.source_type == "local"
    assert norm.title == "Indian Institute of Science AI Lab"
    assert norm.url == "https://iisc.ac.in"
    assert "4.9★" in norm.snippet
    assert norm.published_at is None  # no fabrication of timestamp


def test_normalize_report_batch():
    engine = EvidenceEngine()
    jobs_out = JobsEngineResult(
        query="ML Jobs",
        results=[
            JobResultItem(title="ML Intern", company_name="TCS", link=None),
            JobResultItem(title="AI Researcher", company_name="Microsoft", link="https://msft.com/job"),
        ]
    )
    report = EngineExecutionReport(
        engine="google_jobs",
        query="ML Jobs",
        status="completed",
        result_count=2,
        output=jobs_out,
    )

    items = engine.normalize_report(report, analysis_id="an-42")
    assert len(items) == 2
    assert items[0].url is None  # null preserved
    assert items[1].url == "https://msft.com/job"
