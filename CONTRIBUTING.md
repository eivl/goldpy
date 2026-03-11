# Contributing

## Development setup

Install the project and dev dependencies with `uv`:

```bash
uv sync --group dev
```

Run the CLI locally:

```bash
uv run goldpy price
```

Run tests:

```bash
uv run --group dev pytest
uv run --group dev coverage run -m pytest
uv run --group dev coverage report -m
```

The repository currently expects 100% test coverage. If behavior changes, tests
should change with it.

## Style

- Keep the code small and direct
- Prefer explicit names over clever shortcuts
- Validate upstream data with Pydantic
- Keep CLI output stable unless there is a strong reason to change it

## Commits

- Write clear commit messages
- If Codex contributes to a commit, include:

```text
Co-authored-by: OpenAI Codex <codex@openai.com>
```

## Releases

Releases are driven by Git tags like `v0.1.0`. Pushing a matching tag triggers
the GitHub Actions release workflow, which publishes to PyPI through trusted
publishing.

Recommended release flow:

```bash
uv version --bump patch
git commit -am "Bump version to $(uv version --short)"
git tag "v$(uv version --short)"
git push origin main --tags
```

If PyPI trusted publishing is not configured yet for this repository, add a
publisher on PyPI with:

- Owner: `eivl`
- Repository: `goldpy`
- Workflow: `release.yml`
- Environment: `pypi`

The workflow already uses `pypa/gh-action-pypi-publish`, so no PyPI API token
is needed once trusted publishing is set up.
