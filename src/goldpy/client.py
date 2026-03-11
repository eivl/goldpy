"""HTTP client for Swissquote quote retrieval."""

from __future__ import annotations

from typing import Any

import httpx

from goldpy.models import RawQuote

BASE_URL = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument"


class GoldpyError(Exception):
    """Base application error."""


class QuoteRequestError(GoldpyError):
    """Raised when an upstream HTTP request fails."""


class QuoteValidationError(GoldpyError):
    """Raised when the upstream response shape is invalid."""


class SwissquoteClient:
    """Thin HTTP wrapper around the Swissquote quote endpoint."""

    def __init__(self, timeout: float = 10.0, http_client: httpx.Client | None = None) -> None:
        self.timeout = timeout
        self._http_client = http_client

    def fetch(self, pair: str) -> list[RawQuote]:
        url = f"{BASE_URL}/{pair}"
        try:
            response = self._client.get(url, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise QuoteRequestError(f"Request failed for {pair}: {exc}") from exc

        payload: Any = response.json()
        try:
            return [RawQuote.model_validate(item) for item in payload]
        except Exception as exc:  # pragma: no cover - exercised in tests via pydantic error types
            raise QuoteValidationError("Unexpected response schema.") from exc

    @property
    def _client(self) -> httpx.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx.Client()
