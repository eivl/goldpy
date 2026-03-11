# Examples

This page shows a few realistic ways to run `goldpy`, along with the kind of
output you can expect back.

## Run from the repository with `uv`

If you are inside the project checkout:

```bash
uv run goldpy price
```

Example output:

```{literalinclude} snippets/price-default.txt
:language: text
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

```{literalinclude} snippets/price-json-prime.json
:language: json
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

```{literalinclude} snippets/price-list-options.json
:language: json
```

## Filter by platform and spread profile

```bash
goldpy price --platform SwissquoteCapitalMarkets --spread-profile prime
```
