"""Tests for search trend intelligence (SEARCH INTEREST) and SerpApi caching."""
import pytest

from app.services.evidence_engine import EvidenceEngine
from app.services.search_cache import SearchCache
from app.services.serpapi.trends import TrendResultItem, TrendDataPoint
from app.services.trend_intelligence import TrendIntelligenceEngine, TrendTimelinePoint


def _item(values):
    pts = [TrendDataPoint(date=f"w{i}", value=v) for i, v in enumerate(values)]
    return TrendResultItem(query="AI jobs", average_interest=sum(values) / len(values), timeline_data=pts)


def test_trend_evidence_is_labelled_search_interest():
    ev = EvidenceEngine.normalize_trends_item(_item([10, 20, 40, 80]), "a1", geo="IN")
    assert ev.source_type == "trend"
    assert "SEARCH INTEREST" in ev.snippet
    assert ev.raw_data["interest_label"] == "SEARCH INTEREST"
    assert ev.raw_data["geo"] == "IN"
    assert ev.raw_data["time_range"]
    assert ev.raw_data["trend_direction"] == "rising"
    assert "not job availability" in ev.snippet


def test_trend_direction_falling_and_stable():
    falling = EvidenceEngine.normalize_trends_item(_item([80, 70, 30, 20]), "a1")
    stable = EvidenceEngine.normalize_trends_item(_item([50, 50, 51, 49]), "a1")
    assert falling.raw_data["trend_direction"] == "falling"
    assert stable.raw_data["trend_direction"] == "stable"


def test_insufficient_data_direction():
    pts = [TrendTimelinePoint(date="x", value=5)]
    assert TrendIntelligenceEngine._classify_direction(pts) == "insufficient_data"


def test_cache_key_is_deterministic_and_case_insensitive():
    k1 = SearchCache.make_key("google_trends", "AI Jobs", "IN", {"data_type": "TIMESERIES"})
    k2 = SearchCache.make_key("google_trends", "ai jobs ", "in", {"data_type": "TIMESERIES"})
    assert k1 == k2


def test_cache_hit_and_expiry():
    cache = SearchCache(ttl_seconds=60)
    key = SearchCache.make_key("google_trends", "x")
    assert cache.get(key) is None
    cache.set(key, {"a": 1})
    assert cache.get(key) == {"a": 1}
    assert cache.stats["hits"] == 1 and cache.stats["misses"] == 1

    expired = SearchCache(ttl_seconds=0)
    expired.set(key, {"a": 1})
    assert expired.get(key) is None
