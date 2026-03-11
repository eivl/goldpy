"""Sphinx configuration for goldpy."""

from __future__ import annotations

import sys
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "goldpy"
author = "eivl"
copyright = "2026, eivl"

pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
release = pyproject["project"]["version"]
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
html_theme = "sphinx_rtd_theme"

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
