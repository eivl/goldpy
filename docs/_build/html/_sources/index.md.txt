# goldpy documentation

`goldpy` is a small CLI for checking Swissquote precious metal quotes from the terminal.

```{toctree}
:maxdepth: 2
:caption: Contents

usage
examples
selection
api/index
readthedocs
```

## What this documentation covers

- How to install and run the CLI
- How quote selection works
- What Python modules make up the package

## Quick start

```bash
uv sync --group dev --group docs
uv run --group docs sphinx-build -b html docs docs/_build/html
```
