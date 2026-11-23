# Installation

## From PyPI

The easiest way to install `cdindex-parser` is from the Python Package Index (PyPI):

```bash
pip install cdindex-parser
```

This requires Python 3.10 or newer.

## From Source

You can clone the repository and install it in editable mode:

```bash
git clone https://github.com/chriskyfung/cdindex-parser.git
cd cdindex-parser
pip install -e .
```

Or install with the development extras to run tests and linting:

```bash
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.10
- No runtime dependencies — pure Python standard library

## Development Extras

The `dev` extra installs tools for testing, linting, type checking, and packaging:

| Extra | Purpose |
|---|---|
| `.[dev]` | `pytest`, `ruff`, `mypy`, `build`, `twine`, `pre-commit` |
| `.[docs]` | `mkdocs-material`, `mkdocstrings[python]` |

Install both:

```bash
pip install -e ".[dev,docs]"
```
