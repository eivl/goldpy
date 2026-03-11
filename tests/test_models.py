from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from goldpy.models import NormalizedQuote, PriceSelection, RawQuote


def test_raw_quote_model_parses_response(sample_payload: list[dict]) -> None:
    quote = RawQuote.model_validate(sample_payload[0])

    assert quote.topo.platform == "SwissquoteCapitalMarkets"
    assert quote.spread_profile_prices[0].spread_profile == "premium"
    assert quote.spread_profile_prices[1].mid == Decimal("5177.500")
    assert quote.spread_profile_prices[2].spread == Decimal("0.504")
    assert quote.timestamp == datetime(2026, 3, 11, 15, 24, 18, 815000, tzinfo=UTC)


def test_normalized_quote_json_encodes_decimals() -> None:
    quote = NormalizedQuote(
        pair="XAU/USD",
        bid=Decimal("1.1"),
        ask=Decimal("1.2"),
        mid=Decimal("1.15"),
        timestamp=datetime(2026, 3, 11, tzinfo=UTC),
        selection_mode="aggregate",
        sources_considered=2,
        bid_selection=PriceSelection(
            platform="A", server="B", spread_profile="prime", value=Decimal("1.1")
        ),
        ask_selection=PriceSelection(
            platform="A", server="B", spread_profile="prime", value=Decimal("1.2")
        ),
    )

    payload = quote.model_dump_json()

    assert '"bid":"1.1"' in payload
    assert '"ask":"1.2"' in payload
