"""HTTP client helpers for Swissquote quote retrieval.

The client layer aims to do one job well: ask Swissquote for raw quote data
and turn the response into validated application models. Everything beyond
that belongs in the service layer.
"""

from __future__ import annotations

from typing import Any

import httpx

from goldpy.models import RawQuote

BASE_URL = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument"


class GoldpyError(Exception):
    """Base class for application-specific errors."""


class QuoteRequestError(GoldpyError):
    """Raised when the upstream HTTP request fails."""


class QuoteValidationError(GoldpyError):
    """Raised when the upstream response cannot be validated."""


class SwissquoteClient:
    """Fetch raw quotes from the Swissquote public endpoint.

    :param timeout:
        Request timeout in seconds.
    :param http_client:
        Optional preconfigured :class:`httpx.Client`. Passing one is useful in
        tests and when a caller wants to manage connection reuse explicitly.
    """

    def __init__(self, timeout: float = 10.0, http_client: httpx.Client | None = None) -> None:
        self.timeout = timeout
        self._http_client = http_client

    def fetch(self, pair: str) -> list[RawQuote]:
        """Fetch and validate quotes for an instrument pair.

        :param pair:
            Instrument pair in ``BASE/QUOTE`` form, for example ``XAU/USD``.
        :returns:
            A list of validated :class:`goldpy.models.RawQuote` objects.
        :raises QuoteRequestError:
            If the HTTP request fails or returns a non-success status code.
        :raises QuoteValidationError:
            If Swissquote returns data that does not match the expected schema.
        """
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
        """Return the configured HTTP client.

        If no client was injected, a fresh :class:`httpx.Client` is created on
        demand. That keeps the implementation simple, even if it is not trying
        to be a full connection-management abstraction.
        """
        if self._http_client is not None:
            return self._http_client
        return httpx.Client()
