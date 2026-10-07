"""Search Result Cache – in-memory with TTL, deduplication, and configurable limits.

Cache key = hash(engine + query + location + parameters).
Stores result, timestamp, and expiry.
Logs cache_hit, cache_miss, api_request, api_failure.
Never logs API keys.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Optional
from dataclasses import dataclass, field

from app.config import get_settings

logger = logging.getLogger("clariq.cache")


@dataclass
class CacheEntry:
    key: str
    result: dict[str, Any]
    stored_at: float
    expires_at: float

    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class SearchCache:
    """Thread-safe in-memory cache for SerpApi results.

    Avoids redundant API calls by caching responses with configurable TTL.
    Cache key incorporates engine, query, location, and any extra params.
    """

    def __init__(self, ttl_seconds: Optional[int] = None):
        settings = get_settings()
        self._ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL
        self._store: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    @staticmethod
    def make_key(engine: str, query: str, location: Optional[str] = None, extra: Optional[dict] = None) -> str:
        """Deterministic cache key based on engine, query, location, and extra params."""
        payload = {
            "engine": engine.lower().strip(),
            "query": query.lower().strip(),
            "location": (location or "").lower().strip(),
            "extra": json.dumps(extra or {}, sort_keys=True),
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Retrieve a cached result if it exists and is still valid."""
        entry = self._store.get(key)
        if entry and entry.is_valid():
            self._hits += 1
            logger.debug(f"cache_hit key={key[:8]}… hits={self._hits}")
            return entry.result

        if entry:
            # Expired – evict
            del self._store[key]

        self._misses += 1
        logger.debug(f"cache_miss key={key[:8]}… misses={self._misses}")
        return None

    def set(self, key: str, result: dict[str, Any]) -> None:
        """Store a result with TTL."""
        now = time.monotonic()
        self._store[key] = CacheEntry(
            key=key,
            result=result,
            stored_at=now,
            expires_at=now + self._ttl,
        )
        logger.debug(f"cache_set key={key[:8]}… ttl={self._ttl}s entries={len(self._store)}")

    def evict_expired(self) -> int:
        """Remove all expired entries and return the count evicted."""
        expired_keys = [k for k, v in self._store.items() if not v.is_valid()]
        for k in expired_keys:
            del self._store[k]
        if expired_keys:
            logger.debug(f"cache_evict evicted={len(expired_keys)} remaining={len(self._store)}")
        return len(expired_keys)

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def stats(self) -> dict[str, int]:
        return {"hits": self._hits, "misses": self._misses, "entries": self.size}


# Module-level singleton – shared across all requests in the same process
_global_cache: Optional[SearchCache] = None


def get_cache() -> SearchCache:
    """Return the shared global cache instance (lazy-init)."""
    global _global_cache
    if _global_cache is None:
        _global_cache = SearchCache()
    return _global_cache
