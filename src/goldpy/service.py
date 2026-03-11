"""Quote normalization and selection logic."""

from __future__ import annotations

from dataclasses import dataclass

from goldpy.client import GoldpyError
from goldpy.models import NormalizedQuote, PriceSelection, RawQuote, SpreadProfilePrice


class QuoteSelectionError(GoldpyError):
    """Raised when no quote matches the requested filters."""


@dataclass(frozen=True)
class CandidatePrice:
    platform: str
    server: str
    spread_profile: str
    bid: object
    ask: object
    timestamp: object
    spread: object
    mid: object

    @classmethod
    def from_raw(cls, quote: RawQuote, price: SpreadProfilePrice) -> "CandidatePrice":
        return cls(
            platform=quote.topo.platform,
            server=quote.topo.server,
            spread_profile=price.spread_profile,
            bid=price.bid,
            ask=price.ask,
            timestamp=quote.timestamp,
            spread=price.spread,
            mid=price.mid,
        )


def normalize_pair(pair: str) -> str:
    cleaned = pair.strip().upper()
    parts = [part for part in cleaned.split("/") if part]
    if len(parts) != 2 or any(len(part) < 3 for part in parts):
        raise QuoteSelectionError("Pair must look like BASE/QUOTE, for example XAU/USD.")
    return "/".join(parts)


def select_quote(
    pair: str,
    quotes: list[RawQuote],
    platform: str | None = None,
    spread_profile: str | None = None,
) -> NormalizedQuote:
    candidates = _filter_candidates(quotes, platform=platform, spread_profile=spread_profile)
    best_bid = max(candidates, key=lambda item: item.bid)
    best_ask = min(candidates, key=lambda item: item.ask)
    latest_timestamp = max(candidate.timestamp for candidate in candidates)
    return NormalizedQuote(
        pair=normalize_pair(pair),
        bid=best_bid.bid,
        ask=best_ask.ask,
        mid=(best_bid.bid + best_ask.ask) / 2,
        timestamp=latest_timestamp,
        selection_mode="aggregate",
        sources_considered=len(candidates),
        bid_selection=PriceSelection(
            platform=best_bid.platform,
            server=best_bid.server,
            spread_profile=best_bid.spread_profile,
            value=best_bid.bid,
        ),
        ask_selection=PriceSelection(
            platform=best_ask.platform,
            server=best_ask.server,
            spread_profile=best_ask.spread_profile,
            value=best_ask.ask,
        ),
    )


def select_tightest_quote(
    pair: str,
    quotes: list[RawQuote],
    platform: str | None = None,
    spread_profile: str | None = None,
) -> NormalizedQuote:
    candidates = _filter_candidates(quotes, platform=platform, spread_profile=spread_profile)
    chosen = min(candidates, key=lambda item: (item.spread, -item.mid))
    return NormalizedQuote(
        pair=normalize_pair(pair),
        bid=chosen.bid,
        ask=chosen.ask,
        mid=chosen.mid,
        timestamp=chosen.timestamp,
        selection_mode="tightest",
        sources_considered=len(candidates),
        bid_selection=PriceSelection(
            platform=chosen.platform,
            server=chosen.server,
            spread_profile=chosen.spread_profile,
            value=chosen.bid,
        ),
        ask_selection=PriceSelection(
            platform=chosen.platform,
            server=chosen.server,
            spread_profile=chosen.spread_profile,
            value=chosen.ask,
        ),
    )


def available_platforms(quotes: list[RawQuote]) -> list[str]:
    return sorted({quote.topo.platform for quote in quotes})


def available_spread_profiles(quotes: list[RawQuote]) -> list[str]:
    return sorted(
        {
            price.spread_profile
            for quote in quotes
            for price in quote.spread_profile_prices
        }
    )


def _filter_candidates(
    quotes: list[RawQuote],
    platform: str | None,
    spread_profile: str | None,
) -> list[CandidatePrice]:
    candidates: list[CandidatePrice] = []
    for quote in quotes:
        if platform and quote.topo.platform != platform:
            continue
        for price in quote.spread_profile_prices:
            if spread_profile and price.spread_profile != spread_profile:
                continue
            candidates.append(CandidatePrice.from_raw(quote, price))
    if not candidates:
        raise QuoteSelectionError("No quotes matched the requested filters.")
    return candidates
