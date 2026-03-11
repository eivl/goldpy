"""Pydantic models used throughout ``goldpy``.

These models draw a line between what the upstream API sends and what the rest
of the application wants to work with. The raw models stay close to the
Swissquote payload, while the normalized model is shaped for CLI output.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer


class QuoteTopo(BaseModel):
    """Describe where a quote came from.

    :ivar platform:
        Trading platform name reported by Swissquote.
    :ivar server:
        Specific server identifier for that platform.
    """

    platform: str
    server: str


class SpreadProfilePrice(BaseModel):
    """Represent one spread-profile price entry from the upstream payload.

    :ivar spread_profile:
        Spread profile name, such as ``prime``.
    :ivar bid_spread:
        Spread component applied on the bid side.
    :ivar ask_spread:
        Spread component applied on the ask side.
    :ivar bid:
        Bid price for this profile.
    :ivar ask:
        Ask price for this profile.
    """

    spread_profile: str = Field(alias="spreadProfile")
    bid_spread: Decimal = Field(alias="bidSpread")
    ask_spread: Decimal = Field(alias="askSpread")
    bid: Decimal
    ask: Decimal

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def mid(self) -> Decimal:
        """Return the midpoint between :attr:`bid` and :attr:`ask`."""
        return (self.bid + self.ask) / Decimal("2")

    @computed_field
    @property
    def spread(self) -> Decimal:
        """Return the raw spread for the quote."""
        return self.ask - self.bid


class RawQuote(BaseModel):
    """Represent one raw quote source from Swissquote.

    :ivar topo:
        Metadata about the platform and server that produced the quote.
    :ivar spread_profile_prices:
        Available prices for each spread profile exposed by the source.
    :ivar ts:
        Source timestamp in Unix milliseconds.
    """

    topo: QuoteTopo
    spread_profile_prices: list[SpreadProfilePrice] = Field(alias="spreadProfilePrices")
    ts: int

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def timestamp(self) -> datetime:
        """Return :attr:`ts` converted to a timezone-aware UTC datetime."""
        return datetime.fromtimestamp(self.ts / 1000, tz=UTC)


class PriceSelection(BaseModel):
    """Describe how one side of the displayed quote was chosen.

    :ivar platform:
        Platform that supplied the selected value.
    :ivar server:
        Server that supplied the selected value.
    :ivar spread_profile:
        Spread profile attached to the selected value.
    :ivar value:
        The chosen numeric price.
    """

    platform: str
    server: str
    spread_profile: str
    value: Decimal


class NormalizedQuote(BaseModel):
    """Represent the quote shape returned by the service layer.

    This is the object the CLI prints. It keeps the numbers together with just
    enough provenance to explain where the bid and ask came from.

    :ivar pair:
        Normalized instrument pair.
    :ivar bid:
        Selected bid price.
    :ivar ask:
        Selected ask price.
    :ivar mid:
        Midpoint shown to the user.
    :ivar timestamp:
        Timestamp used for the final result.
    :ivar selection_mode:
        Strategy name used to select the quote.
    :ivar sources_considered:
        Number of candidate prices considered after filtering.
    :ivar bid_selection:
        Provenance for the chosen bid.
    :ivar ask_selection:
        Provenance for the chosen ask.
    """

    pair: str
    bid: Decimal
    ask: Decimal
    mid: Decimal
    timestamp: datetime
    selection_mode: str
    sources_considered: int
    bid_selection: PriceSelection
    ask_selection: PriceSelection

    model_config = ConfigDict()

    @field_serializer("bid", "ask", "mid")
    def serialize_decimal_fields(self, value: Decimal) -> str:
        """Serialize decimal price fields as strings for stable JSON output."""
        return str(value)
