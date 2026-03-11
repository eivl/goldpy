from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from goldpy import cli
from goldpy.models import RawQuote

runner = CliRunner()
DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "snippets"


def _build_quotes(sample_payload: list[dict]) -> list[RawQuote]:
    return [RawQuote.model_validate(item) for item in sample_payload]


class StubClient:
    def __init__(self, quotes: list[RawQuote]) -> None:
        self._quotes = quotes

    def fetch(self, pair: str) -> list[RawQuote]:
        return self._quotes


@pytest.fixture(autouse=True)
def stub_client(sample_payload: list[dict], monkeypatch: pytest.MonkeyPatch) -> None:
    quotes = _build_quotes(sample_payload)
    monkeypatch.setattr(cli, "SwissquoteClient", lambda timeout=10.0: StubClient(quotes))


def test_default_example_matches_cli_output() -> None:
    result = runner.invoke(cli.app, ["price"])

    assert result.exit_code == 0
    assert result.stdout == (DOCS_DIR / "price-default.txt").read_text()


def test_json_example_matches_cli_output() -> None:
    result = runner.invoke(cli.app, ["price", "--json", "--spread-profile", "prime"])

    assert result.exit_code == 0
    assert result.stdout == (DOCS_DIR / "price-json-prime.json").read_text()


def test_list_options_example_matches_cli_output() -> None:
    result = runner.invoke(cli.app, ["price", "--list-options"])

    assert result.exit_code == 0
    assert result.stdout == (DOCS_DIR / "price-list-options.json").read_text()
