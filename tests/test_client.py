from __future__ import annotations

import httpx
import pytest

from goldpy.client import QuoteRequestError, QuoteValidationError, SwissquoteClient


def test_fetch_parses_quotes(sample_payload: list[dict]) -> None:
    client = SwissquoteClient(
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=sample_payload))
        )
    )

    quotes = client.fetch("XAU/USD")

    assert len(quotes) == 3
    assert quotes[0].topo.server == "Live7"


def test_fetch_raises_request_error_on_http_failure() -> None:
    client = SwissquoteClient(
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(503, json={"detail": "down"}))
        )
    )

    with pytest.raises(QuoteRequestError):
        client.fetch("XAU/USD")


def test_fetch_raises_validation_error_on_bad_schema() -> None:
    client = SwissquoteClient(
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"unexpected": True}))
        )
    )

    with pytest.raises(QuoteValidationError):
        client.fetch("XAU/USD")


def test_default_client_property_builds_httpx_client(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[object] = []

    class DummyClient:
        pass

    monkeypatch.setattr(httpx, "Client", lambda: created.append(DummyClient()) or created[-1])

    client = SwissquoteClient()

    assert client._client is created[0]
