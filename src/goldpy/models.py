"""Pydantic models for Swissquote quotes and normalized output."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer


class QuoteTopo(BaseModel):
    """Source metadata for a quote feed."""

    platform: str
    server: str


class SpreadProfilePrice(BaseModel):
    """One price point for a spread profile."""

    spread_profile: str = Field(alias="spreadProfile")
    bid_spread: Decimal = Field(alias="bidSpread")
    ask_spread: Decimal = Field(alias="askSpread")
    bid: Decimal
    ask: Decimal

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")

    @computed_field
    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid


class RawQuote(BaseModel):
    """One Swissquote quote source."""

    topo: QuoteTopo
    spread_profile_prices: list[SpreadProfilePrice] = Field(alias="spreadProfilePrices")
    ts: int

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.ts / 1000, tz=UTC)


class PriceSelection(BaseModel):
    """How a side of the quote was selected."""

    platform: str
    server: str
    spread_profile: str
    value: Decimal


class NormalizedQuote(BaseModel):
    """Normalized quote returned by the service layer."""

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
        return str(value)
