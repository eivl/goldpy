from __future__ import annotations

import json
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from goldpy import cli
from goldpy.client import QuoteRequestError
from goldpy.models import RawQuote

runner = CliRunner()


def _build_quotes(sample_payload: list[dict]) -> list[RawQuote]:
    return [RawQuote.model_validate(item) for item in sample_payload]


class StubClient:
    def __init__(self, quotes: list[RawQuote] | None = None, error: Exception | None = None) -> None:
        self._quotes = quotes or []
        self._error = error

    def fetch(self, pair: str) -> list[RawQuote]:
        if self._error:
            raise self._error
        return self._quotes


@pytest.fixture(autouse=True)
def reset_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient())


def test_price_command_human_output(sample_payload: list[dict], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient(_build_quotes(sample_payload)))

    result = runner.invoke(cli.app, ["price"])

    assert result.exit_code == 0
    assert "Pair: XAU/USD" in result.stdout
    assert "Mode: aggregate" in result.stdout
    assert "Sources considered: 9" in result.stdout


def test_price_command_json_output(sample_payload: list[dict], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient(_build_quotes(sample_payload)))

    result = runner.invoke(cli.app, ["price", "--json", "--spread-profile", "prime"])

    payload = json.loads(result.stdout)

    assert result.exit_code == 0
    assert payload["pair"] == "XAU/USD"
    assert payload["selection_mode"] == "aggregate"
    assert payload["bid"] == "5177.183"


def test_price_command_lists_options(sample_payload: list[dict], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient(_build_quotes(sample_payload)))

    result = runner.invoke(cli.app, ["price", "--list-options"])

    payload = json.loads(result.stdout)

    assert result.exit_code == 0
    assert payload["platforms"][0] == "AT"
    assert payload["spread_profiles"][-1] == "standard"


def test_price_command_supports_tightest_mode(sample_payload: list[dict], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient(_build_quotes(sample_payload)))

    result = runner.invoke(cli.app, ["price", "--mode", "tightest"])

    assert result.exit_code == 0
    assert "Mode: tightest" in result.stdout


def test_price_command_surfaces_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli,
        "SwissquoteClient",
        lambda timeout=10.0: StubClient(error=QuoteRequestError("boom")),
    )

    result = runner.invoke(cli.app, ["price"])

    assert result.exit_code == 1
    assert "Error: boom" in result.stderr


def test_format_quote_renders_all_sections() -> None:
    formatted = cli._format_quote(
        cli.select_quote(
            "XAU/USD",
            _build_quotes(
                [
                    {
                        "topo": {"platform": "A", "server": "S"},
                        "spreadProfilePrices": [
                            {
                                "spreadProfile": "prime",
                                "bidSpread": 1,
                                "askSpread": 1,
                                "bid": Decimal("1.1"),
                                "ask": Decimal("1.2"),
                            }
                        ],
                        "ts": 1773242658815,
                    }
                ]
            ),
        )
    )

    assert "Best bid from: A/S (prime)" in formatted


def test_print_error_returns_exit_code() -> None:
    assert cli._print_error("nope") == 1
