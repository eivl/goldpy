"""Quote normalization and selection logic.

This module is where the raw upstream feed becomes something easier to reason
about. It handles pair validation, filtering, and the two quote selection
strategies exposed by the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass

from goldpy.client import GoldpyError
from goldpy.models import NormalizedQuote, PriceSelection, RawQuote, SpreadProfilePrice


class QuoteSelectionError(GoldpyError):
    """Raised when quote selection cannot produce a result."""


@dataclass(frozen=True)
class CandidatePrice:
    """Internal flattened quote candidate used during selection.

    The upstream payload nests prices under each source. For selection logic it
    is easier to work with one record per source/profile combination.
    """

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
        """Build a candidate from a raw quote and one spread-profile price.

        :param quote:
            Raw quote source metadata.
        :param price:
            One spread-profile price entry from that source.
        :returns:
            A flattened :class:`CandidatePrice` instance.
        """
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
    """Normalize and validate an instrument pair string.

    The function accepts small variations in user input, trims whitespace, and
    uppercases both sides before validating the final ``BASE/QUOTE`` shape.

    :param pair:
        Pair supplied by the caller.
    :returns:
        Normalized pair string.
    :raises QuoteSelectionError:
        If the pair does not look like ``BASE/QUOTE``.
    """
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
    """Select an aggregate quote from the available candidates.

    The aggregate strategy chooses the best bid and best ask independently,
    then computes a midpoint from those two values. I like this mode because it
    answers the simple question of where the market edges currently sit.

    :param pair:
        Instrument pair being requested.
    :param quotes:
        Raw quote sources returned by the client.
    :param platform:
        Optional platform filter.
    :param spread_profile:
        Optional spread profile filter.
    :returns:
        A normalized quote using the aggregate strategy.
    :raises QuoteSelectionError:
        If filtering leaves no valid candidates.
    """
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
    """Select the tightest single quote from the available candidates.

    This strategy keeps bid and ask together from one source/profile pair.
    When two candidates share the same spread, the higher midpoint wins.

    :param pair:
        Instrument pair being requested.
    :param quotes:
        Raw quote sources returned by the client.
    :param platform:
        Optional platform filter.
    :param spread_profile:
        Optional spread profile filter.
    :returns:
        A normalized quote using the tightest strategy.
    :raises QuoteSelectionError:
        If filtering leaves no valid candidates.
    """
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
    """Return the sorted list of distinct platforms in the raw quotes."""
    return sorted({quote.topo.platform for quote in quotes})


def available_spread_profiles(quotes: list[RawQuote]) -> list[str]:
    """Return the sorted list of distinct spread profiles in the raw quotes."""
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
    """Filter raw quotes into flattened candidates ready for selection.

    :param quotes:
        Raw quotes from the upstream API.
    :param platform:
        Optional platform filter.
    :param spread_profile:
        Optional spread profile filter.
    :returns:
        Candidate prices matching the requested filters.
    :raises QuoteSelectionError:
        If no candidates remain after filtering.
    """
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
