# Examples

This page shows a few realistic ways to run `goldpy`, along with the kind of
output you can expect back.

## Run from the repository with `uv`

If you are inside the project checkout:

```bash
uv run goldpy price
```

Example output:

```text
Pair: XAU/USD
Mode: aggregate
Bid: 3021.45
Ask: 3021.73
Mid: 3021.59
Timestamp: 2026-03-11T13:42:10.123000+00:00
Sources considered: 8
Best bid from: SwissquoteCapitalMarkets/live-1 (prime)
Best ask from: SwissquoteBank/live-2 (prime)
```

## Run without installing permanently via `uvx`

```bash
uvx goldpy-cli price
```

That is a good fit when you want a quick quote on a machine where `uv` is
already available but you do not want to manage a long-lived tool install.

## Install as a tool with `uv`

```bash
uv tool install goldpy-cli
goldpy price
```

This is the most direct option if you already use `uv` for Python tools.

## Install with `pipx`

```bash
pipx install goldpy-cli
goldpy price
```

This is a good option if you prefer `pipx` as your tool runner and want the
CLI available globally in its own isolated environment.

## JSON output

```bash
uvx goldpy-cli price --json
```

Example output:

```json
{
  "pair": "XAU/USD",
  "bid": "3021.45",
  "ask": "3021.73",
  "mid": "3021.59",
  "timestamp": "2026-03-11T13:42:10.123000Z",
  "selection_mode": "aggregate",
  "sources_considered": 8,
  "bid_selection": {
    "platform": "SwissquoteCapitalMarkets",
    "server": "live-1",
    "spread_profile": "prime",
    "value": "3021.45"
  },
  "ask_selection": {
    "platform": "SwissquoteBank",
    "server": "live-2",
    "spread_profile": "prime",
    "value": "3021.73"
  }
}
```

## Different pair

```bash
goldpy price --pair XAU/EUR
```

## Tightest quote

```bash
goldpy price --mode tightest
```

In this mode, the bid and ask come from the same source/profile combination.

## Inspect available options

```bash
goldpy price --list-options
```

Example output:

```json
{
  "pair": "XAU/USD",
  "platforms": [
    "SwissquoteBank",
    "SwissquoteCapitalMarkets"
  ],
  "spread_profiles": [
    "premium",
    "prime",
    "standard"
  ]
}
```

## Filter by platform and spread profile

```bash
goldpy price --platform SwissquoteCapitalMarkets --spread-profile prime
```
