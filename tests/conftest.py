from __future__ import annotations

from decimal import Decimal

import pytest

from goldpy.models import RawQuote


@pytest.fixture()
def sample_payload() -> list[dict]:
    return [
        {
            "topo": {"platform": "SwissquoteCapitalMarkets", "server": "Live7"},
            "spreadProfilePrices": [
                {
                    "spreadProfile": "premium",
                    "bidSpread": 25.40,
                    "askSpread": 25.40,
                    "bid": 5177.171,
                    "ask": 5177.829,
                },
                {
                    "spreadProfile": "prime",
                    "bidSpread": 24.40,
                    "askSpread": 24.40,
                    "bid": 5177.181,
                    "ask": 5177.819,
                },
                {
                    "spreadProfile": "elite",
                    "bidSpread": 17.70,
                    "askSpread": 17.70,
                    "bid": 5177.248,
                    "ask": 5177.752,
                },
            ],
            "ts": 1773242658815,
        },
        {
            "topo": {"platform": "SwissquoteLtd", "server": "Live5"},
            "spreadProfilePrices": [
                {
                    "spreadProfile": "premium",
                    "bidSpread": 25.60,
                    "askSpread": 25.60,
                    "bid": 5177.169,
                    "ask": 5177.831,
                },
                {
                    "spreadProfile": "prime",
                    "bidSpread": 24.20,
                    "askSpread": 24.20,
                    "bid": 5177.183,
                    "ask": 5177.817,
                },
                {
                    "spreadProfile": "elite",
                    "bidSpread": 17.70,
                    "askSpread": 17.70,
                    "bid": 5177.248,
                    "ask": 5177.752,
                },
            ],
            "ts": 1773242658815,
        },
        {
            "topo": {"platform": "AT", "server": "AT"},
            "spreadProfilePrices": [
                {
                    "spreadProfile": "standard",
                    "bidSpread": 27.00,
                    "askSpread": 27.00,
                    "bid": 5177.155,
                    "ask": 5177.845,
                },
                {
                    "spreadProfile": "premium",
                    "bidSpread": 25.65,
                    "askSpread": 25.65,
                    "bid": 5177.169,
                    "ask": 5177.832,
                },
                {
                    "spreadProfile": "prime",
                    "bidSpread": 24.25,
                    "askSpread": 24.25,
                    "bid": 5177.183,
                    "ask": 5177.818,
                },
            ],
            "ts": 1773242658815,
        },
    ]


@pytest.fixture()
def sample_quotes(sample_payload: list[dict]) -> list[RawQuote]:
    return [RawQuote.model_validate(item) for item in sample_payload]


@pytest.fixture()
def sample_decimals() -> tuple[Decimal, Decimal]:
    return Decimal("5177.248"), Decimal("5177.752")
