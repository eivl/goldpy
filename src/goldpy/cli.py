"""Command-line interface for ``goldpy``.

The CLI stays intentionally direct. It exposes one command that answers the
question the project was built around, while still giving enough switches to
inspect the quote sources when needed.
"""

from __future__ import annotations

import json
from enum import Enum

import typer

from goldpy.client import GoldpyError, SwissquoteClient
from goldpy.models import NormalizedQuote, RawQuote
from goldpy.service import (
    available_platforms,
    available_spread_profiles,
    normalize_pair,
    select_quote,
    select_tightest_quote,
)

app = typer.Typer(no_args_is_help=True, add_completion=False)


class SelectionMode(str, Enum):
    """Selection strategies exposed by the CLI."""

    aggregate = "aggregate"
    tightest = "tightest"


@app.callback()
def main() -> None:
    """Provide Swissquote precious metal quote utilities."""


@app.command()
def price(
    pair: str = typer.Option("XAU/USD", help="Instrument pair, for example XAU/USD."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
    platform: str | None = typer.Option(None, help="Restrict quotes to one platform."),
    spread_profile: str | None = typer.Option(None, "--spread-profile", help="Restrict quotes to one spread profile."),
    mode: SelectionMode = typer.Option(
        SelectionMode.aggregate,
        "--mode",
        help="How to choose the displayed quote.",
        case_sensitive=False,
    ),
    timeout: float = typer.Option(10.0, min=0.1, help="Request timeout in seconds."),
    list_options: bool = typer.Option(
        False,
        "--list-options",
        help="List platforms and spread profiles available for the requested pair.",
    ),
) -> None:
    """Fetch and print a precious metal quote.

    :param pair:
        Instrument pair in ``BASE/QUOTE`` form.
    :param json_output:
        When ``True``, print structured JSON instead of terminal text.
    :param platform:
        Optional platform filter.
    :param spread_profile:
        Optional spread profile filter.
    :param mode:
        Quote selection strategy.
    :param timeout:
        Request timeout in seconds.
    :param list_options:
        When ``True``, print available platforms and spread profiles for the
        requested pair instead of a quote.
    :raises typer.Exit:
        Raised with exit code ``1`` when quote retrieval or selection fails.
    """

    normalized_pair = normalize_pair(pair)
    client = SwissquoteClient(timeout=timeout)
    try:
        quotes = client.fetch(normalized_pair)
        if list_options:
            payload = {
                "pair": normalized_pair,
                "platforms": available_platforms(quotes),
                "spread_profiles": available_spread_profiles(quotes),
            }
            typer.echo(json.dumps(payload, indent=2))
            return

        quote = _select(
            pair=normalized_pair,
            quotes=quotes,
            platform=platform,
            spread_profile=spread_profile,
            mode=mode,
        )
    except GoldpyError as exc:
        raise typer.Exit(code=_print_error(str(exc)))

    if json_output:
        typer.echo(quote.model_dump_json(indent=2))
        return

    typer.echo(_format_quote(quote))


def _select(
    pair: str,
    quotes: list[RawQuote],
    platform: str | None,
    spread_profile: str | None,
    mode: SelectionMode,
) -> NormalizedQuote:
    """Dispatch to the requested selection strategy.

    :param pair:
        Normalized instrument pair.
    :param quotes:
        Raw quotes from the client.
    :param platform:
        Optional platform filter.
    :param spread_profile:
        Optional spread profile filter.
    :param mode:
        Selected CLI mode.
    :returns:
        The normalized quote chosen by the selected strategy.
    """
    if mode is SelectionMode.aggregate:
        return select_quote(pair, quotes, platform=platform, spread_profile=spread_profile)
    return select_tightest_quote(pair, quotes, platform=platform, spread_profile=spread_profile)


def _format_quote(quote: NormalizedQuote) -> str:
    """Format a normalized quote for terminal output."""
    return "\n".join(
        [
            f"Pair: {quote.pair}",
            f"Mode: {quote.selection_mode}",
            f"Bid: {quote.bid}",
            f"Ask: {quote.ask}",
            f"Mid: {quote.mid}",
            f"Timestamp: {quote.timestamp.isoformat()}",
            f"Sources considered: {quote.sources_considered}",
            (
                "Best bid from: "
                f"{quote.bid_selection.platform}/{quote.bid_selection.server} "
                f"({quote.bid_selection.spread_profile})"
            ),
            (
                "Best ask from: "
                f"{quote.ask_selection.platform}/{quote.ask_selection.server} "
                f"({quote.ask_selection.spread_profile})"
            ),
        ]
    )


def _print_error(message: str) -> int:
    """Print an error message to stderr and return the exit status."""
    typer.echo(f"Error: {message}", err=True)
    return 1
