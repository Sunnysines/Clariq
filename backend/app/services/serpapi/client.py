"""SerpApi HTTP Client with retry, timeout, error handling, and response validation."""
from __future__ import annotations

import logging
from typing import Any, Optional
import httpx

from app.config import get_settings

logger = logging.getLogger("clariq.serpapi")


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
    """Async client for interacting with SerpApi."""

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.SERPAPI_API_KEY
        self.timeout = timeout if timeout is not None else settings.REQUEST_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else settings.MAX_RETRIES

    def _validate_api_key(self) -> None:
        if not self.api_key or not self.api_key.strip():
            raise SerpApiAuthError(
                "SERPAPI_API_KEY is not configured. Please supply a valid SerpApi API key."
            )

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a query against SerpApi with retry and validation."""
        self._validate_api_key()

        request_params = {
            **params,
            "api_key": self.api_key,
            "output": "json",
        }

        engine = params.get("engine", "google")
        query = params.get("q", "")
        logger.info(f"Executing SerpApi engine '{engine}' with query: '{query}'")

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.BASE_URL, params=request_params)

                if response.status_code == 401 or response.status_code == 403:
                    error_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    raise SerpApiAuthError(
                        f"Authentication failed with SerpApi ({response.status_code}): {error_json.get('error', 'Invalid API key')}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                if response.status_code == 429:
                    error_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    raise SerpApiRateLimitError(
                        f"Rate limit exceeded or quota exhausted ({response.status_code}): {error_json.get('error', 'Too many requests')}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                if response.status_code >= 400:
                    error_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    raise SerpApiError(
                        f"SerpApi HTTP error {response.status_code}: {error_json.get('error', response.text)}",
                        status_code=response.status_code,
                        error_details=error_json,
                    )

                data = response.json()
                if "error" in data:
                    raise SerpApiError(f"SerpApi returned error payload: {data['error']}", error_details=data)

                return data

            except (httpx.TimeoutException, httpx.ConnectTimeout) as exc:
                last_error = SerpApiTimeoutError(f"SerpApi request timed out after {self.timeout}s (attempt {attempt})")
                logger.warning(f"Timeout on SerpApi '{engine}' query '{query}' (attempt {attempt}/{self.max_retries + 1})")
            except (SerpApiAuthError, SerpApiRateLimitError):
                # Don't retry authentication or rate limit errors
                raise
            except httpx.RequestError as exc:
                last_error = SerpApiError(f"Network error querying SerpApi: {str(exc)}")
                logger.warning(f"Network error on SerpApi '{engine}' (attempt {attempt}/{self.max_retries + 1}): {exc}")
            except Exception as exc:
                if isinstance(exc, SerpApiError):
                    raise
                last_error = SerpApiError(f"Unexpected error: {str(exc)}")
                logger.warning(f"Error on SerpApi '{engine}' (attempt {attempt}): {exc}")

        if last_error:
            raise last_error

        raise SerpApiError(f"Failed to execute SerpApi query after {self.max_retries + 1} attempts")
