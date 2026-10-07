"""SerpApi HTTP Client with retry, timeout, error handling, caching, and response validation.

Security:
- API key is NEVER logged.
- Only engine name and query are written to logs.
- Errors do not expose the key in tracebacks.
"""
from __future__ import annotations

import logging
from typing import Any, Optional
import httpx

from app.config import get_settings
from app.services.search_cache import get_cache, SearchCache

logger = logging.getLogger("clariq.serpapi")

# httpx logs the full request URL (including api_key) at INFO level – never allow that.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class SerpApiError(Exception):
    """Base exception for SerpApi interactions."""

    def __init__(self, message: str, status_code: Optional[int] = None, error_details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_details = error_details or {}


class SerpApiAuthError(SerpApiError):
    """Raised when SerpApi API key is missing or invalid."""
    pass


class SerpApiTimeoutError(SerpApiError):
    """Raised when request times out."""
    pass


class SerpApiRateLimitError(SerpApiError):
    """Raised when request is rate limited or quota exceeded."""
    pass


class SerpApiClient:
    """Async client for interacting with SerpApi with integrated caching."""

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        cache: Optional[SearchCache] = None,
    ):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.SERPAPI_API_KEY
        self.timeout = timeout if timeout is not None else settings.REQUEST_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else settings.MAX_RETRIES
        self._cache = cache if cache is not None else get_cache()

    def _validate_api_key(self) -> None:
        if not self.api_key or not self.api_key.strip():
            raise SerpApiAuthError(
                "SERPAPI_API_KEY is not configured. Please supply a valid SerpApi API key."
            )

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a query against SerpApi with cache lookup, retry, and validation.

        Logging is intentionally limited to engine/query — API key is never written.
        """
        self._validate_api_key()

        engine = params.get("engine", "google")
        query = params.get("q", "")
        location = params.get("location") or params.get("geo", "")

        # Strip sensitive fields before making cache key
        extra_safe = {k: v for k, v in params.items() if k not in ("api_key", "q", "engine", "location", "geo")}
        cache_key = SearchCache.make_key(engine, query, location, extra_safe)

        # --- Cache lookup ---
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info(f"cache_hit engine='{engine}' query='{query}'")
            return cached

        logger.info(f"api_request engine='{engine}' query='{query}'")

        request_params = {
            **params,
            "api_key": self.api_key,
            "output": "json",
        }

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.BASE_URL, params=request_params)

                if response.status_code in (401, 403):
                    error_json = response.json() if "application/json" in response.headers.get("content-type", "") else {}
                    raise SerpApiAuthError(
                        f"Authentication failed with SerpApi ({response.status_code}): {error_json.get('error', 'Invalid API key')}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                if response.status_code == 429:
                    error_json = response.json() if "application/json" in response.headers.get("content-type", "") else {}
                    raise SerpApiRateLimitError(
                        f"Rate limit exceeded or quota exhausted ({response.status_code}): {error_json.get('error', 'Too many requests')}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                if response.status_code >= 400:
                    error_json = response.json() if "application/json" in response.headers.get("content-type", "") else {}
                    raise SerpApiError(
                        f"SerpApi HTTP error {response.status_code}: {error_json.get('error', 'Unknown error')}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                data = response.json()
                if "error" in data:
                    raise SerpApiError(f"SerpApi returned error payload: {data['error']}", error_details=data)

                # Cache successful result
                self._cache.set(cache_key, data)
                logger.info(f"api_success engine='{engine}' query='{query}' cached=True")
                return data

            except (httpx.TimeoutException, httpx.ConnectTimeout):
                last_error = SerpApiTimeoutError(f"SerpApi request timed out after {self.timeout}s (attempt {attempt})")
                logger.warning(f"api_timeout engine='{engine}' attempt={attempt}/{self.max_retries + 1}")
            except (SerpApiAuthError, SerpApiRateLimitError):
                # Do not retry auth or rate-limit errors
                raise
            except httpx.RequestError as exc:
                last_error = SerpApiError(f"Network error querying SerpApi: {str(exc)}")
                logger.warning(f"api_failure engine='{engine}' attempt={attempt}/{self.max_retries + 1} reason=network")
            except SerpApiError:
                raise
            except Exception as exc:
                last_error = SerpApiError(f"Unexpected error: {str(exc)}")
                logger.warning(f"api_failure engine='{engine}' attempt={attempt} reason=unexpected")

        logger.error(f"api_failure engine='{engine}' query='{query}' all_attempts_exhausted=True")
        if last_error:
            raise last_error
        raise SerpApiError(f"Failed to execute SerpApi query after {self.max_retries + 1} attempts")
