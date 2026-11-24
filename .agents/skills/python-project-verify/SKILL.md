---
name: python-project-verify
description: Run the full verification suite for a Python project and report pass/fail. Use whenever the user asks to verify, validate, run checks, check CI readiness, or before shipping/releasing. Make sure to use this skill whenever the user mentions verifying a project, running checks, validating before release, or checking CI readiness, even if they don't explicitly list every check.
---

# python-project-verify

Run the complete verification suite for a Python project: lint, format, type check, tests with coverage gate, build, metadata validation, docs build, CLI smoke test, and end-to-end API call. Report pass/fail for each check and interpret failures. This skill captures the verification checklist from `cdindex2-parser`'s AGENTS.md.

---

## When to use

- "Verify this project"
- "Run all checks"
- "Is this ready to ship?"
- "Validate before release"
- "Check CI readiness"
- "Run the full verification sweep"

---

## Prerequisites

- Python ≥ 3.10
- `pip install -e ".[dev]"` already run (dev extras installed)
- `build`, `twine`, `mkdocs` available

---

## Phase 1: Lint (ruff check)

Run ruff lint on source and tests:

```bash
ruff check src/ tests/
```

**Pass criteria:** 0 errors, exit code 0.

**Common failures and fixes:**

| Error | Meaning | Fix |
|---|---|---|
| `D100` | Missing module docstring | Add `"""..."""` at top of module |
| `D101` | Missing class docstring | Add docstring after class declaration |
| `D103` | Missing function docstring | Add docstring to public function |
| `N818` | Exception name should end in `Error` | Rename `LineCountMismatch` → `LineCountMismatchError` |
| `RUF002` | Non-breaking hyphen in docstring | Replace `‑` (U+2011) with `-` |
| `F821` | Undefined name | Add missing import |
| `E501` | Line too long (>88) | Wrap the line or shorten |

**Pitfall:** `ruff check --fix` auto-fixes some issues (import sorting, unused imports) but not docstring issues. Always re-run after `--fix`.

---

## Phase 2: Format check (ruff format)

Check that code is formatted according to ruff:

```bash
ruff format --check src/ tests/
```

**Pass criteria:** "X files already formatted" or no diff output.

**If not formatted:** Run `ruff format src/ tests/` to auto-format, then re-check.

**Pitfall:** `ruff format` may reflow long docstrings and import blocks. Always re-run `ruff check` after formatting because formatting can expose new lint issues.

---

## Phase 3: Type check (mypy)

Run mypy in strict mode on source:

```bash
mypy src
```

**Pass criteria:** "Success: no issues found in X source files", exit code 0.

**Common failures and fixes:**

| Error | Meaning | Fix |
|---|---|---|
| `no-untyped-def` | Missing type annotations | Add type hints to function parameters and return |
| `no-untyped-call` | Calling untyped function in typed context | Add type hints to the called function |
| `arg-type` | Argument type mismatch | Ensure argument type matches parameter annotation |
| `return-value` | Incompatible return type | Ensure return value matches annotated return type |
| `type-arg` | Missing type arguments for generic | Use `dict[str, object]` not `dict`, `list[Entry]` not `list` |

**Pitfall:** `dict[str, object]` loses type info for field access. Build dataclass instances directly instead of through intermediate dicts.

**Pitfall:** `mypy strict = true` must be configured in `pyproject.toml` `[tool.mypy]`.

---

## Phase 4: Tests with coverage gate

Run pytest with branch coverage:

```bash
pytest tests/ --cov=cdindex2_parser --cov-branch --cov-report=term-missing
```

**Pass criteria:**
- All tests pass (exit code 0)
- Coverage ≥ 80% branch (`fail_under = 80` in `pyproject.toml` `[tool.coverage.report]`)

**Common failures:**

| Issue | Meaning | Fix |
|---|---|---|
| `SystemExit` | `argparse` calls `sys.exit()` | Wrap `main()` calls in `pytest.raises(SystemExit)` and assert `.code` |
| `ImportError` | Missing import in conftest or test | Add import to `tests/conftest.py` |
| Coverage < 80% | Branch coverage below gate | Add tests for uncovered branches (error paths, edge cases) |

**Pitfall:** Tests that call CLI `--help` or `--version` will raise `SystemExit` because `argparse` calls `sys.exit()`. Use `pytest.raises(SystemExit)`.

**Pitfall:** Coverage is measured on the installed package. Install with `pip install -e .` first.

---

## Phase 5: Build

Build sdist and wheel:

```bash
python -m build
```

**Pass criteria:** Produces `dist/*.whl` and `dist/*.tar.gz`, exit code 0.

**Common failures:**

| Issue | Meaning | Fix |
|---|---|---|
| `InvalidConfigError` | License classifiers conflict with PEP 639 | Remove `License ::` classifier when using `license = "MIT"` |
| `InvalidConfigError` | `authors[0].email` must be valid email | Use a valid email address, not `[EMAIL]` placeholder |
| Build fails | `setuptools < 77` with PEP 639 license | Ensure `build-system.requires = ["setuptools>=77"]` |

**Pitfall:** The `[tool.setuptools.packages.find]` must have `where = ["src"]` for src layout.

---

## Phase 6: Metadata validation

Validate distribution metadata:

```bash
twine check dist/*
```

**Pass criteria:** `Checking dist/*.whl: PASSED` and `Checking dist/*.tar.gz: PASSED`, exit code 0.

**Common failures:** Same as build phase — license format, author email, missing fields.

---

## Phase 7: CLI smoke test

Install the wheel in a fresh venv and smoke test:

```bash
python -m venv /tmp/venv
/tmp/venv/bin/pip install dist/*.whl
/tmp/venv/bin/cdindex2-parser --help
/tmp/venv/bin/python -c "import cdindex2_parser; print(cdindex2_parser.__version__)"
```

**Pass criteria:**
- `cdindex2-parser --help` exits 0 and shows usage
- Import works and prints version
- Exit code 0 for all commands

**Pitfall:** The wheel must include `py.typed` for typed packages. Check `[tool.setuptools.package-data]`.

**Pitfall:** The console script entry point must be `cdindex2-parser = "cdindex2_parser.cli:main"`.

---

## Phase 8: Docs build

Build MkDocs documentation in strict mode:

```bash
mkdocs build --strict
```

**Pass criteria:** "Documentation built in X seconds", exit code 0.

**Common failures:**

| Issue | Meaning | Fix |
|---|---|---|
| `mkdocstrings` can't find symbol | Symbol not importable | Install package first (`pip install -e .`); check symbol path |
| Non-breaking hyphen in docstring | `RUF002` equivalent in docs | Replace `‑` with `-` |
| Missing mkdocstrings handler | `mkdocstrings[python]` not installed | Install docs extras (`pip install -e ".[docs]"`) |

---

## Phase 9: End-to-end API call

Parse a real `.IDX`/`.FILE` pair and assert on the `Catalog`:

```python
import sys, tempfile, pathlib

sys.path.insert(0, "src")
from cdindex2_parser import parse_catalog, resolve_input_path

# Test rstrip fix (the silent data-corruption bug)
for p in ["MyID.IDX", "GAME.IDX", "DISK.IDX"]:
    idx, fle = resolve_input_path(p)
    assert idx == p and fle == p[:-4] + ".FILE", f"FAIL: {p}"

# End-to-end parse
tmpdir = pathlib.Path(tempfile.mkdtemp())
catalog = parse_catalog(tmpdir / "test.IDX", encoding="utf-8")
assert len(catalog) > 0
for entry in catalog:
    assert hasattr(entry, "path")
    assert hasattr(entry, "is_dir")
    assert hasattr(entry, "size_bytes")
```

**Pass criteria:** All assertions pass, no exceptions.

**Pitfall:** Always call `parse_catalog()` end-to-end, not just leaf helpers like `parse_file_line`. Import success ≠ runtime correctness.

---

## Interpretation and reporting

Report results as a table:

| Phase | Command | Status | Notes |
|---|---|---|---|
| Lint | `ruff check src/ tests/` | PASS/FAIL | |
| Format | `ruff format --check` | PASS/FAIL | |
| Type check | `mypy src` | PASS/FAIL | |
| Tests | `pytest tests/ --cov` | PASS/FAIL | Coverage: X% |
| Build | `python -m build` | PASS/FAIL | |
| Metadata | `twine check dist/*` | PASS/FAIL | |
| CLI smoke | venv + `cdindex2-parser --help` | PASS/FAIL | |
| Docs | `mkdocs build --strict` | PASS/FAIL | |
| End-to-end | `parse_catalog()` round-trip | PASS/FAIL | |

**Overall:** PASS if all phases pass; FAIL if any phase fails. Do not proceed to release with any FAIL.
