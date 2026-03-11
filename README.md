# goldpy

[![Tests](https://github.com/eivl/goldpy/actions/workflows/test.yml/badge.svg)](https://github.com/eivl/goldpy/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/goldpy.svg)](https://pypi.org/project/goldpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`goldpy` is a command line tool for people who want a fast answer to a simple
question: what is gold trading at right now?

I wanted something small, readable, and honest about the data it shows. The
CLI pulls live quote data from Swissquote, validates the response with
Pydantic, and prints either terminal-friendly output or structured JSON.

The default behavior uses an aggregate quote strategy. It finds the best bid
and best ask across the returned quote sources and profiles, then calculates a
mid price from those values. If you want something more specific, you can
filter by platform, spread profile, or switch selection mode.

## What it does

- Fetches live precious metal quotes from Swissquote
- Defaults to `XAU/USD`
- Supports other instrument pairs like `XAU/EUR`
- Prints either readable terminal output or JSON
- Lets you inspect available platforms and spread profiles
- Ships as a normal Python package managed with `uv`

## Installation

For local development:

```bash
uv sync --group dev
```

Once published to PyPI, the intended install will be:

```bash
uv tool install goldpy
```

## Usage

Basic quote:

```bash
uv run goldpy price
```

JSON output:

```bash
uv run goldpy price --json
```

Different pair:

```bash
uv run goldpy price --pair XAU/EUR
```

Specific source options:

```bash
uv run goldpy price --platform SwissquoteCapitalMarkets --spread-profile prime
```

List available platforms and spread profiles for a pair:

```bash
uv run goldpy price --list-options
```

Use the tightest single quote instead of the aggregate view:

```bash
uv run goldpy price --mode tightest
```

## Development

Run tests:

```bash
uv run --group dev pytest
```

Run coverage:

```bash
uv run --group dev coverage run -m pytest
uv run --group dev coverage report -m
```

The test suite is configured to require 100% coverage.

## License

MIT. See [LICENSE](LICENSE).
