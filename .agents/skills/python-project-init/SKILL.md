---
name: python-project-init
description: Initialize a new Python package project from scratch. Use when starting a new Python library project. Make sure to use this skill whenever the user mentions creating a new Python library, starting a new Python project, or initializing a new package.
---

# python-project-init

Initialize a new Python package project from scratch with a modern src-layout, typed API, console script entry point, and complete packaging metadata. This skill covers the initial setup phase of a new Python project.

---

## When to use

- "Create a new Python package"
- "Start a new Python library project"
- "Initialize a new Python project"
- "Create a new pip-installable library"

---

## Prerequisites

- Python ≥ 3.10 installed
- `setuptools >=77` available
- Git repository initialized

---

## Step 1: Create project structure

```bash
mkdir -p src/<package_name>/tests
```

**Package naming convention:** Use lowercase with hyphens for the project name (e.g., `cdindex-parser`), and underscores for the package directory (e.g., `cdindex_parser`).

---

## Step 2: Create pyproject.toml

Use setuptools with PEP 639 license metadata:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "<package-name>"
version = "0.1.0"
description = "Brief description of your package"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
license-files = ["LICENSE"]
authors = [{name = "Your Name", email = "your.email@example.com"}]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Topic :: Utilities",
    "Typing :: Typed",
]
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5", "mypy>=1.11", "ruff>=0.6", "build>=1.2", "twine>=5", "pre-commit>=3.8"]
docs = ["mkdocs-material>=9.5", "mkdocstrings[python]>=0.26"]

[project.urls]
Homepage = "https://github.com/<username>/<repo>"
Repository = "https://github.com/<username>/<repo>"

[project.scripts]
<cli-name> = "<package_name>.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["<package_name>*"]

[tool.setuptools.package-data]
<package_name> = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
branch = true
source = ["<package_name>"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

---

## Step 3: Create package skeleton

Create the package directory and files:

**`src/<package_name>/__init__.py`** — Public API exports:

```python
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("<package-name>")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    # Public API symbols go here
    "__version__",
]
```

**`src/<package_name>/__main__.py`** — Module entry point:

```python
"""Module entry point for python -m <package-name>."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

**`src/<package_name>/py.typed`** — Empty file, PEP 561 marker:

```bash
touch src/<package_name>/py.typed
```

---

## Step 4: Create core modules

Create the core modules based on your project's needs. Typical modules include:

- **cli.py** — argparse CLI with `--version` and other flags
- **parser.py** — Core parsing logic
- **models.py** — Frozen dataclasses for data models
- **errors.py** — Typed exception hierarchy

---

## Step 5: Create tests directory

```bash
mkdir -p tests
```

Create `tests/conftest.py` with shared fixtures and individual test files per module.

---

## Step 6: Create project metadata files

- `README.md` — Project overview, quick start, usage examples
- `LICENSE` — MIT license text
- `README.md` — Project badges and links
- `.gitignore` — Python-specific ignores
- `.gitattributes` — Line ending normalization
- `.pre-commit-config.yaml` — Pre-commit hooks

---

## Step 7: Verify the package

```bash
pip install -e .
<package-name> --help
python -c "import <package_name>; print(<package_name>.__version__)"
python -m build
twine check dist/*
```

---

## Commit atomically

Commit in logical steps:

1. `chore(repo): initialize project structure`
2. `build!: adopt setuptools with PEP 639 license`
3. `refactor(core): implement core parsing logic`
4. `refactor(cli): add argparse CLI`
5. `test: add initial test suite`
6. `docs: add README and API documentation`
7. `ci: add GitHub Actions CI workflow`
