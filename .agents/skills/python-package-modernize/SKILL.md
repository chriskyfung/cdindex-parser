---
name: python-package-modernize
description: Transform a legacy Python script into a publishable, importable src-layout package. Use whenever the user wants to modernize, restructure, package, make pip-installable, or add pyproject.toml / CLI / typing to an existing script. Make sure to use this skill whenever the user mentions modernizing a script, converting to a package, adding a console script, setting up pyproject.toml, or adopting the src layout, even if they don't explicitly ask for all of these.
---

# python-package-modernize

Transform a legacy Python script (single-file, root-level) into a modern, publishable Python package with a `src/` layout, typed API, console script entry point, and complete packaging metadata. This skill captures the full modernization performed on `cdindex-parser` from root script → importable PyPI-ready package.

---

## When to use

- "Turn this script into a package"
- "Make it pip-installable"
- "Adopt the src layout"
- "Add a console script entry point"
- "Add typing / dataclasses to this script"
- "Modernize the project packaging"
- "Add pyproject.toml with PEP 639 license"

---

## Prerequisites

Before starting, confirm:

- Python ≥ 3.10 is available (for `setuptools >=77` PEP 639 license support).
- `setuptools >=77` is installed (required for `license = "MIT"` + `license-files`).
- `build` and `twine` are available for verification.
- The user has decided on the package name, CLI command name, and Python version floor.

---

## Step 1: Audit the existing script

Identify all the pieces that need extracting:

1. **Entry point function** — usually `main()` reading `sys.argv` directly.
2. **Pure parsing logic** — functions that transform input data (no I/O side effects).
3. **Path resolution** — any logic that derives `.IDX`/`.FILE` paths from a base name.
4. **Export/output writing** — CSV/JSON writers.
5. **Error handling** — any `assert`, `ValueError`, or bare exceptions used for control flow.

**Pitfall:** Do not copy-paste the script into the new package. Use `git mv` to preserve history, then refactor in place.

**Example (before → after):**

```python
# BEFORE: root script, sys.argv coupled, assert for control flow
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    input_path = sys.argv[1]
    out_path = sys.argv[2]
    assert len(file_lines) == len(idx_lines), "line count mismatch"
    match_and_dump(input_path, out_path)
```

```python
# AFTER: src/cdindex_parser/cli.py, typed, testable
def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ...
    return 0
```

---

## Step 2: Create the src layout

1. Create the package directory:
   ```bash
   mkdir -p src/cdindex_parser
   ```

2. Move the existing script into the package using `git mv` (preserves history):
   ```bash
   git mv decode_cdindex.py src/cdindex_parser/parser.py
   ```

3. Create the package skeleton:

   **`src/cdindex_parser/__init__.py`** — public API exports + `__version__`:
   ```python
   from importlib.metadata import PackageNotFoundError, version
   from .exporters import to_csv, to_json
   from .models import Catalog, Entry, FileRecord, NameRecord
   from .parser import parse_catalog, resolve_input_path

   try:
       __version__ = version("cdindex-parser")
   except PackageNotFoundError:
       __version__ = "0.0.0+unknown"

   __all__ = [
       "Catalog",
       "Entry",
       "FileRecord",
       "NameRecord",
       "parse_catalog",
       "resolve_input_path",
       "to_csv",
       "to_json",
       "__version__",
   ]
   ```

   **`src/cdindex_parser/__main__.py`** — `python -m cdindex_parser` entry point:
   ```python
   """Module entry point for python -m cdindex_parser."""

   from .cli import main

   if __name__ == "__main__":
       raise SystemExit(main())
   ```

   **`src/cdindex_parser/py.typed`** — empty file, PEP 561 marker for typed packages:
   ```bash
   touch src/cdindex_parser/py.typed
   ```

**Pitfall:** `__main__.py` must guard `raise SystemExit(main())` with `if __name__ == "__main__":`, otherwise importing the module triggers program exit.

---

## Step 3: Refactor into modules

Split the monolith into responsibility-separated modules:

| Module | Responsibility |
|---|---|
| `errors.py` | Typed exception hierarchy (`CDIndexError`, `*Error` suffix) |
| `models.py` | Frozen dataclasses (`Catalog`, `Entry`, `FileRecord`, `NameRecord`) |
| `parser.py` | Pure parsing: `parse_catalog`, `parse_file_line`, `parse_name_line`, `decode_dos_datetime`, `resolve_input_path` |
| `tree.py` | Stack-based path reconstruction (`build_paths`) |
| `exporters.py` | `to_csv`, `to_json`, `iter_rows` |
| `cli.py` | argparse CLI with `--encoding`, `--format`, `--version` |

**Pitfall:** Do not mix refactoring with behavior changes. Keep each module commit atomic — one logical change per commit.

**Pitfall:** Replace `assert` statements used for control flow (line-count mismatch, indent mismatch) with typed exceptions. `assert` is stripped under `python -O`.

**Pitfall:** Replace `str.rstrip('.IDX')` (treats argument as a character set — corrupts `MyID.IDX` → `My`) with proper suffix stripping using `endswith` + slicing, case-insensitive.

**Pitfall:** Do not use `Path.with_suffix()` on dotted base names (e.g. `archive.1.IDX` → `archive.IDX`). Use `str(base) + ".IDX"` instead.

---

## Step 4: Write pyproject.toml

Use **setuptools** with PEP 639 license metadata:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "cdindex-parser"
version = "0.3.0"
description = "Parse CD Index 2 IDX/FILE catalogs into CSV/JSON"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
license-files = ["LICENSE"]
authors = [{name = "Chris K.Y. Fung", email = "8746768+chriskyfung@users.noreply.github.com"}]
keywords = ["cd-index", "cdindex", "parser", "csv", "json"]
classifiers = [
    "Development Status :: 4 - Beta",
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
Homepage = "https://github.com/chriskyfung/cdindex-parser"
Repository = "https://github.com/chriskyfung/cdindex-parser"

[project.scripts]
cdindex-parser = "cdindex_parser.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["cdindex_parser*"]

[tool.setuptools.package-data]
cdindex_parser = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
branch = true
source = ["cdindex_parser"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

**Pitfall:** `license = {file = "LICENSE"}` is deprecated (PEP 639). Use `license = "MIT"` + `license-files = ["LICENSE"]`.

**Pitfall:** `license = "MIT"` + `license-files` requires **setuptools ≥ 77**. Enforce this in `build-system.requires`.

**Pitfall:** `License :: OSI Approved :: MIT License` classifier conflicts with `license = "MIT"` expression format — remove the classifier when using PEP 639 license expression.

---

## Step 5: Verify the package

1. Install in editable mode:
   ```bash
   pip install -e . --break-system-packages
   ```

2. Test the CLI:
   ```bash
   cdindex-parser --help
   cdindex-parser --version
   ```

3. Test the import:
   ```bash
   python -c "import cdindex_parser; print(cdindex_parser.__version__)"
   ```

4. Build and check:
   ```bash
   python -m build
   twine check dist/*
   ```

**Pitfall:** The console script entry point must point to `cdindex_parser.cli:main`, not `scripts.decode_cdindex:main` (the old root script path).

---

## Step 6: Commit atomically

Split the modernization into atomic commits:

1. `chore(repo): add .gitattributes, fix .gitignore, add pre-commit config`
2. `build!: adopt src layout, PEP 639 license, repair console script`
3. `refactor(core): add package skeleton (__init__, __main__, py.typed)`
4. `refactor(errors): add typed exception hierarchy (*Error suffix)`
5. `refactor(models): replace dict records with frozen slotted dataclasses`
6. `refactor(tree): extract stack-based path reconstruction`
7. `refactor(exporters): add CSV and JSON exporters`
8. `refactor(parser)!: core parsing with rstrip fix, dataclass migration, typed exceptions`
9. `refactor(cli): add argparse CLI with --encoding, --format, --version`
10. `chore(core): remove legacy decode_cdindex.py script`

Each commit must be independently green (builds, imports, CLI works).

---

## Step 7: Final verification

Run the full verification sweep:

```bash
ruff check src/ tests/ && \
ruff format --check src/ tests/ && \
mypy src && \
pytest tests/ --cov=cdindex_parser --cov-branch && \
python -m build && \
twine check dist/* && \
mkdocs build --strict
```

If any check fails, fix it before committing. Do not merge with red checks.
