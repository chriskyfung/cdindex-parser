# AGENTS.md — cdindex2-parser

This file is the single source of truth for AI agents (and humans) working on this repository. Read it before making any change.

---

## Project Overview

**cdindex2-parser** converts legacy `*.IDX` / `*.FILE` catalogs from **CD Index 2** (光碟索引大師) into modern **CSV / JSON**, preserving the full file tree structure, sizes, and modification timestamps.

| Property | Value |
|---|---|
| Language | Python 3 |
| Runtime deps | None (standard library only) |
| Minimum Python | `>=3.10` |
| Package layout | `src/cdindex2_parser/` |
| Console script | `cdindex2-parser` |
| Build backend | `setuptools >=77` |
| License | MIT (PEP 639: `license = "MIT"` + `license-files`) |
| Public entry point | `cdindex2_parser.parse_catalog()` |

Input: `.IDX` (names / tree structure via tab indentation) + `.FILE` (properties `[D|F]<size>.<timestamp>`).  
Output: CSV with columns `FullPath,IsDir,SizeBytes,MtimeStr`, or JSON with schema version 1.

---

## Repository Layout

```
cdindex2-parser/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # lint / test matrix / build / CI gate
│   │   ├── release.yml     # TestPyPI -> PyPI -> GitHub Release (trusted publishing)
│   │   └── docs.yml        # MkDocs deploy to GitHub Pages
│   ├── dependabot.yml
│   └── ISSUE_TEMPLATE / PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   ├── file-format.md
│   ├── api.md              # mkdocstrings auto-generated reference
│   └── troubleshooting.md
├── mkdocs.yml
├── src/cdindex2_parser/
│   ├── __init__.py         # public API, __version__
│   ├── __main__.py         # python -m cdindex2_parser
│   ├── cli.py              # argparse CLI: --encoding, --format, --version
│   ├── errors.py           # typed exception hierarchy (*Error suffix)
│   ├── exporters.py        # to_csv / to_json / iter_rows
│   ├── models.py           # frozen dataclasses: Catalog, Entry, FileRecord, NameRecord
│   ├── parser.py           # parse_catalog, parse_file_line, parse_name_line, decode_dos_datetime, resolve_input_path
│   ├── tree.py             # stack-based path reconstruction (build_paths)
│   └── py.typed            # PEP 561 marker
├── tests/
│   ├── conftest.py         # fixtures (sample, flat, utf16, big5 pairs)
│   ├── test_parser.py
│   ├── test_tree.py
│   ├── test_exporters.py
│   ├── test_cli.py
│   └── test_errors.py
├── pyproject.toml          # setuptools >=77, PEP 639, classifiers, scripts, coverage
├── README.md
├── CHANGELOG.md            # Keep a Changelog
├── LICENSE
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
└── AGENTS.md               # this file
```

---

## Quick Reference — Commands

Copy-paste these directly.

### Install (editable, with dev extras)
```bash
pip install -e ".[dev,docs]"
```

### Lint + format check
```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

### Type check
```bash
mypy src
```

### Test (with branch coverage gate)
```bash
pytest tests/ --cov=cdindex2_parser --cov-branch --cov-report=term-missing
```
Coverage gate is `fail_under = 80` in `pyproject.toml` `[tool.coverage.report]`.

### Build + publish validation
```bash
python -m build
twine check dist/*
```

### Smoke test the wheel
```bash
python -m venv /tmp/venv
/tmp/venv/bin/pip install dist/*.whl
/tmp/venv/bin/cdindex2-parser --help
/tmp/venv/bin/python -c "import cdindex2_parser; print(cdindex2_parser.__version__)"
```

### Build docs
```bash
mkdocs build --strict
```

### Run everything (single verification sweep)
```bash
ruff check src/ tests/ && \
ruff format --check src/ tests/ && \
mypy src && \
pytest tests/ --cov=cdindex2_parser --cov-branch --cov-report=term-missing && \
python -m build && \
twine check dist/* && \
mkdocs build --strict
```


## Conventions

### Conventional Commits

Format: `<type>(<scope>): <subject>`

| Type | Use for | Examples |
|---|---|---|
| `feat` | New capability | `feat(cli): add --format json` |
| `fix` | Bug fix | `fix(parser): strip IDX/FILE suffixes without corrupting names` |
| `refactor` | Code change, no bug/feature | `refactor(models): dataclasses instead of dicts` |
| `test` | Adding/correcting tests | `test(tree): cover depth reset` |
| `docs` | Documentation only | `docs(api): generate reference with mkdocstrings` |
| `ci` | CI/CD configuration | `ci: add Windows test matrix` |
| `build` | Build/packaging/deps | `build: switch to setuptools >=77` |
| `chore` | Maintenance | `chore(repo): bump version to 0.3.0` |
| `style` | Formatting only | `style: normalize constants` |
| `perf` | Performance | `perf(parser): stream lines instead of readlines` |
| `revert` | Revert previous | `revert(ci): disable codecov upload` |

Rules:
- Subject: imperative mood, lowercase, no trailing period, ≤ 72 chars.
- Breaking change: add `!` after type/scope and a `BREAKING CHANGE:` footer.
- Reference issues: `Refs: #12` in footer.
- No emoji, no `WIP`, no `fixup` on shared branches.
- Squash locally before push (`git rebase --autosquash`).

### Python Style

- Line length **88** (ruff).
- `ruff` select: `E F W I N UP B C4 SIM RUF D PT S`; ignore `D203 D213`.
- `mypy strict = true` on `src/`.
- Dataclasses: `@dataclass(frozen=True, slots=True)`.
- Exceptions: suffix with `Error`, inherit from `CDIndexError`.
- No `assert` for control flow (disabled under `python -O`).
- Type hints on all public functions.
- Docstrings: Google style; required on public modules/classes/functions (`D` ruleset).

---

## Branching & PR Workflow

**Strategy: GitHub Flow.** One short-lived branch per PR into `main`.

Branch naming: `<type>/<short-kebab-description>` (e.g. `fix/path-suffix`, `chore/repo-hygiene`, `feat/ci-matrix`). Lowercase, hyphens, ≤ 50 chars.

Merge policy:
- `refactor/*`, `test/*`: **rebase merge** (preserve atomic history, bisectable).
- `chore/*`, `ci/*`, `docs/*`: **squash merge** (keep `main` clean).
- No merge commits (`allow_merge_commit: false`).

Before merging:
```bash
git fetch origin
git rebase origin/main
# resolve conflicts, re-run full verification
git push --force-with-lease
```

CI gate: branch protection requires the `ci-success` job (aggregates `lint` + `test` + `build`) to pass. Matrix job names may change freely.

---

## Definition of Done (DoD)

Every change must pass this checklist before merging to `main`:

| # | Check | Command |
|---|---|---|
| 1 | Lint clean | `ruff check src/ tests/` → 0 errors |
| 2 | Format clean | `ruff format --check src/ tests/` → clean |
| 3 | Type clean | `mypy src` → 0 errors |
| 4 | Tests pass | `pytest tests/` → green |
| 5 | Coverage gate | `--cov-fail-under=80` passes |
| 6 | Build valid | `python -m build` produces `dist/*.whl` + `*.tar.gz` |
| 7 | Metadata valid | `twine check dist/*` → PASSED |
| 8 | CLI works | `/tmp/venv/bin/cdindex2-parser --help` exits 0 |
| 9 | Import works | `python -c "import cdindex2_parser; print(cdindex2_parser.__version__)"` |
| 10 | Docs build | `mkdocs build --strict` → clean |
| 11 | End-to-end | `parse_catalog()` on a real `.IDX`/`.FILE` pair produces correct CSV/JSON |

Never merge with a red check. `git bisect` must land on a working commit at every step.

---
---

## Known Pitfalls (learned this session)

These are concrete mistakes made during this migration. **Do not repeat them.**

| # | Pitfall | Symptom | Fix |
|---|---|---|---|
| 1 | `str.rstrip('.IDX')` treats arg as a **character set**, corrupting names (`MyID.IDX` → `My`, `GAME.IDX` → `GAM`). | `resolve_input_path` returns wrong base name. | Use `Path.with_suffix()` + explicit `endswith` checks, case-insensitive. |
| 2 | `Path.with_suffix(".IDX")` on `archive.1.IDX` → `archive.IDX` (drops dotted base). | Dotted base names truncated. | Use `str(base) + ".IDX"` instead of `with_suffix`. |
| 3 | `assert` for line-count / indent mismatch is **stripped under `python -O`**. | Checks silently skipped in production. | Typed exceptions (`LineCountMismatchError`, `IndentMismatchError`). |
| 4 | Non-breaking hyphens (`‑`, U+2011) in docstrings. | ruff `RUF002` errors; mkdocstrings build failures. | Use plain hyphen `-` in all docstrings. |
| 5 | `dict[str, object]` loses field types for `Entry` construction. | mypy `arg-type` errors on every field. | Build `Entry` directly from typed records; no intermediate `dict`. |
| 6 | `EncodingError` extends `UnicodeDecodeError` → `__init__` requires **5 args** (`encoding, object, start, end, reason`). | `TypeError: takes exactly 5 arguments` when raising with one arg. | Don't subclass `UnicodeDecodeError` unless you pass all 5 args; use plain `CDIndexError` subclass instead, or pass all 5. |
| 7 | `argparse` calls `sys.exit()` via `SystemExit`. | Tests calling `main(["--help"])` raise `SystemExit` instead of returning. | Wrap `main()` calls in `pytest.raises(SystemExit)` and assert `.code`. |
| 8 | `__main__.py` calls `raise SystemExit(main())` at import time. | Importing `cdindex2_parser.__main__` triggers program exit. | Guard with `if __name__ == "__main__":`. |
| 9 | Shell heredocs / `python3 -c "..."` with nested quotes fail unpredictably. | `unexpected EOF`, `command not found`. | Write multi-line Python/scripts to a `.py` file first, then execute it. |
| 10 | Tests written against `main` branch don't survive rebasing onto `refactor/core`. | Broken imports after branch switch. | Re-verify prior-phase changes survived the new branch before continuing. |

---

## Agent-Specific Guidance

1. **Verify the top-level API end-to-end.** Never stop at leaf helpers (`parse_file_line`, `parse_name_line`). Always call `parse_catalog()` on a real temp `.IDX`/`.FILE` pair and assert on the resulting `Catalog`. Import success ≠ runtime correctness.

2. **Re-verify prior-phase changes survived a new branch.** Branches cut from `main` do not inherit unmerged work. After `git checkout -b <new> main`, re-read every file a previous phase touched (e.g. `.gitignore`, `.gitattributes`) before building on it.

3. **Diff the working tree against this plan section-by-section before declaring done.** For each planned commit/PR, confirm it exists in `git log`. A single 690-line commit is not a substitute for atomic commits.

4. **Delete scratch artifacts before committing.** `pyproject.toml.bak`, `.pytest_cache/`, `__pycache__/`, `dist/`, `build/`, `*.egg-info/` must never be committed.

5. **Run commands from this AGENTS.md, not from memory.** The commands above are the verified, working versions. Re-typing from memory is how typos and quoting bugs creep in.

---

## Adding a New Feature

1. Create branch: `git checkout -b feat/<name> main`
2. Add/change code in `src/cdindex2_parser/`
3. Add tests in `tests/`
4. Update docs in `docs/` if user-facing
5. Update `CHANGELOG.md`
6. Run the full DoD checklist
7. Commit atomically (Conventional Commit format)
8. Open PR; merge via squash/rebase per policy; delete branch