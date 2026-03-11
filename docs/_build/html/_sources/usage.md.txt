# Usage

## Install dependencies

For local documentation work:

```bash
uv sync --group dev --group docs
```

For normal local development without building docs:

```bash
uv sync --group dev
```

## Install the CLI

If you want to use `goldpy` as a tool instead of working on the repository,
these are the most practical options.

### `uv tool install`

```bash
uv tool install goldpy-cli
```

### `uvx`

`uvx` is useful when you want to run the tool without keeping a permanent
installation around:

```bash
uvx goldpy-cli price
```

### `pipx`

```bash
pipx install goldpy-cli
```

## CLI examples

Basic quote:

```bash
uv run goldpy price
```

Installed with `uv`:

```bash
goldpy price
```

Run through `uvx`:

```bash
uvx goldpy-cli price
```

Installed with `pipx`:

```bash
goldpy price
```

Machine-readable JSON:

```bash
uv run goldpy price --json
```

With `uvx`:

```bash
uvx goldpy-cli price --json
```

With `pipx`:

```bash
goldpy price --json
```

Specific instrument pair:

```bash
uv run goldpy price --pair XAU/EUR
```

With `uvx`:

```bash
uvx goldpy-cli price --pair XAU/EUR
```

Specific quote source filters:

```bash
uv run goldpy price --platform SwissquoteCapitalMarkets --spread-profile prime
```

Inspect available platforms and spread profiles:

```bash
uv run goldpy price --list-options
```

Use the tightest single quote:

```bash
uv run goldpy price --mode tightest
```

## Selection modes

`aggregate`
: Uses the best bid and best ask across all matching sources, then calculates the midpoint from those values.

`tightest`
: Picks the single quote with the smallest spread. If spreads tie, the higher midpoint wins.

## Build the docs

```bash
uv run --group docs sphinx-build -b html docs docs/_build/html
```
