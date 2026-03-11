from __future__ import annotations

from decimal import Decimal

import pytest

from goldpy.service import (
    QuoteSelectionError,
    available_platforms,
    available_spread_profiles,
    normalize_pair,
    select_quote,
    select_tightest_quote,
)


def test_normalize_pair_uppercases_and_trims() -> None:
    assert normalize_pair(" xau/usd ") == "XAU/USD"


def test_normalize_pair_rejects_invalid_values() -> None:
    with pytest.raises(QuoteSelectionError):
        normalize_pair("gold")


def test_select_quote_aggregates_best_bid_and_ask(sample_quotes) -> None:
    quote = select_quote("xau/usd", sample_quotes)

    assert quote.selection_mode == "aggregate"
    assert quote.bid == Decimal("5177.248")
    assert quote.ask == Decimal("5177.752")
    assert quote.mid == Decimal("5177.500")
    assert quote.sources_considered == 9
    assert quote.bid_selection.platform == "SwissquoteCapitalMarkets"
    assert quote.ask_selection.platform == "SwissquoteCapitalMarkets"


def test_select_quote_respects_filters(sample_quotes) -> None:
    quote = select_quote(
        "XAU/USD",
        sample_quotes,
        platform="SwissquoteLtd",
        spread_profile="prime",
    )

    assert quote.bid == Decimal("5177.183")
    assert quote.ask == Decimal("5177.817")
    assert quote.sources_considered == 1


def test_select_tightest_quote_prefers_smallest_spread(sample_quotes) -> None:
    quote = select_tightest_quote("XAU/USD", sample_quotes)

    assert quote.selection_mode == "tightest"
    assert quote.bid == Decimal("5177.248")
    assert quote.ask == Decimal("5177.752")
    assert quote.bid_selection.platform == "SwissquoteCapitalMarkets"
    assert quote.ask_selection.platform == "SwissquoteCapitalMarkets"


def test_available_options_are_sorted(sample_quotes) -> None:
    assert available_platforms(sample_quotes) == ["AT", "SwissquoteCapitalMarkets", "SwissquoteLtd"]
    assert available_spread_profiles(sample_quotes) == ["elite", "premium", "prime", "standard"]


def test_select_quote_raises_for_empty_filter_result(sample_quotes) -> None:
    with pytest.raises(QuoteSelectionError):
        select_quote("XAU/USD", sample_quotes, platform="missing")
