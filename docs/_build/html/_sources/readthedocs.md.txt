# Read the Docs

This project is ready for Read the Docs with the repository-level `.readthedocs.yaml` file.

## Expected setup

1. Import the GitHub repository into Read the Docs.
2. Leave the configuration file path as the default `.readthedocs.yaml`.
3. Read the Docs will install the `docs` extra and build from the `docs/` directory.

## Local parity

The local build command matches the configured Read the Docs builder:

```bash
uv run --group docs sphinx-build -b html docs docs/_build/html
```
