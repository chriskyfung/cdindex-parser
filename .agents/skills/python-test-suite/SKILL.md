---
name: python-test-suite
description: Generate a comprehensive pytest suite with fixtures, parametrization, edge cases, and a coverage gate. Use whenever the user asks for tests, test coverage, or pytest. Make sure to use this skill whenever the user mentions writing tests, test coverage, pytest, or adding tests to a project, even if they don't specify the testing framework or coverage requirements.
---

# python-test-suite

Generate a comprehensive pytest suite for a Python package: fixtures (conftest.py), test modules organized by source module, parametrized cases, error-path tests, golden files, and a coverage gate (`fail_under = 80`). This skill captures the test suite implemented for `cdindex-parser` (75 tests, 93% branch coverage).

---

## When to use

- "Write tests"
- "Test coverage"
- "pytest"
- "Add tests"
- "Generate test suite"

---

## Prerequisites

- `pytest`, `pytest-cov`, `coverage[toml]` installed (in `[project.optional-dependencies] dev`)
- `pyproject.toml` `[tool.pytest.ini_options]` configured with `testpaths = ["tests"]`, `pythonpath = ["src"]`
- Package installed: `pip install -e .`

---

## Step 1: Create conftest.py — shared fixtures

`conftest.py` defines reusable fixtures that create temp `.IDX`/`.FILE` pairs. Use `tmp_path` for isolation.

```python
"""Pytest fixtures for cdindex-parser tests."""

from pathlib import Path

import pytest

T = "\t"


def write_pair(tmp_path, base, idx_content, file_content, encoding="utf-8"):
    """Write a .IDX/.FILE pair and return their paths."""
    idx_path = tmp_path / f"{base}.IDX"
    file_path = tmp_path / f"{base}.FILE"
    idx_path.write_text(idx_content, encoding=encoding)
    file_path.write_text(file_content, encoding=encoding)
    return idx_path, file_path


@pytest.fixture
def sample_pair(tmp_path):
    """A simple .IDX/.FILE pair with nested directory structure."""
    idx_content = (
        "Root Folder\n" + T + "File 1-1.txt\n" + T + "File 1-2.txt\n"
        + T + "Sub Folder\n" + T + T + "File 2-1.txt\n"
    )
    file_content = (
        "D0.25482084\n" + T + "F226.25482084\n" + T + "F528.25482084\n"
        + T + "D0.25482084\n" + T + T + "F100.25482084\n"
    )
    return write_pair(tmp_path, "sample", idx_content, file_content)


@pytest.fixture
def flat_pair(tmp_path):
    """A flat .IDX/.FILE pair (no nesting)."""
    idx_content = "File A.txt\nFile B.txt\n"
    file_content = "F100.25482084\nF200.25482084\n"
    return write_pair(tmp_path, "flat", idx_content, file_content)


@pytest.fixture
def utf16_pair(tmp_path):
    """A .IDX/.FILE pair encoded as UTF-16 with BOM."""
    idx_content = "Root Folder\n\tFile.txt\n"
    file_content = "D0.25482084\n\tF100.25482084\n"
    return write_pair(tmp_path, "utf16", idx_content, file_content, encoding="utf-16")


@pytest.fixture
def big5_pair(tmp_path):
    """A .IDX/.FILE pair encoded as Big5 (Traditional Chinese)."""
    idx_content = "Root Folder\n\t\u96fb\u80fd\u6587\u4ef6.txt\n"
    file_content = "D0.25482084\n\tF100.25482084\n"
    return write_pair(tmp_path, "big5", idx_content, file_content, encoding="big5")


@pytest.fixture
def flat_catalog():
    """A simple Catalog with two entries for exporter tests."""
    from datetime import datetime
    from cdindex_parser.models import Catalog, Entry

    return Catalog(
        entries=(
            Entry(

---

## Step 2: Organize tests by source module

Create one test file per source module:

| Test file | Covers |
|---|---|
| `tests/test_parser.py` | `parse_catalog`, `parse_file_line`, `parse_name_line`, `decode_dos_datetime`, `resolve_input_path` |
| `tests/test_tree.py` | `build_paths` — nesting, siblings, depth reset |
| `tests/test_exporters.py` | `to_csv`, `to_json`, `iter_rows` — schema, quoting, encoding |
| `tests/test_cli.py` | `build_parser`, `main` — flags, exit codes, end-to-end |
| `tests/test_errors.py` | Exception hierarchy, catchability |

**Pitfall:** Test file names must start with `test_` for pytest discovery.

**Pitfall:** Group tests into classes (`TestParser`, `TestTree`, etc.) for organization and shared setup.

---

## Step 3: Write parser tests

Cover parsing functions and edge cases:

```python
class TestResolveInputPath:
    """Tests for resolve_input_path — the fix for the rstrip corruption bug."""

    def test_preserves_corruptible_names(self):
        """The old rstrip() corrupted MyID.IDX → My and GAME.IDX → GAM."""
        for p in ["MyID.IDX", "GAME.IDX", "DISK.IDX"]:
            idx, fle = resolve_input_path(p)
            assert idx == p
            assert fle == p[:-4] + ".FILE"

    def test_lowercase_suffix(self):
        idx, fle = resolve_input_path("mydisk.idx")
        assert idx == "mydisk.IDX"
        assert fle == "mydisk.FILE"

    def test_with_directory(self):
        idx, fle = resolve_input_path("/home/user/data.mydisk.IDX")
        assert idx == "/home/user/data.mydisk.IDX"
        assert fle == "/home/user/data.mydisk.FILE"


class TestParseCatalog:
    """End-to-end tests for parse_catalog."""

    def test_flat_pair(self, flat_pair):
        idx_path, _ = flat_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        assert len(catalog) == 2

    def test_nested_structure(self, sample_pair):
        idx_path, _ = sample_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        assert len(catalog) == 5
        paths = [e.path for e in catalog]
        assert "Root Folder" in paths
        assert "Root Folder/File 1-1.txt" in paths

    def test_utf16_encoding(self, utf16_pair):
        idx_path, _ = utf16_pair
        catalog = parse_catalog(idx_path, encoding="utf-16")
        assert len(catalog) == 2

    def test_big5_encoding(self, big5_pair):
        idx_path, _ = big5_pair
        catalog = parse_catalog(idx_path, encoding="big5")
        assert "\u96fb\u80fd\u6587\u4ef6" in catalog.entries[1].name

    def test_line_count_mismatch(self, tmp_path):
        (tmp_path / "bad.IDX").write_text("A\nB\n", encoding="utf-8")
        (tmp_path / "bad.FILE").write_text("D0.25482084\n", encoding="utf-8")
        from cdindex_parser.errors import LineCountMismatchError
        with pytest.raises(LineCountMismatchError):
            parse_catalog(tmp_path / "bad", encoding="utf-8")

    def test_missing_file(self, tmp_path):
        from cdindex_parser.errors import InputNotFoundError
        with pytest.raises(InputNotFoundError):
            parse_catalog(tmp_path / "nonexistent", encoding="utf-8")
```

**Pitfall:** Always test error paths (line count mismatch, missing file, malformed record, indent mismatch) — not just happy path.

**Pitfall:** Test encodings explicitly (utf-16, big5) since the tool targets legacy CJK files.


---

## Step 4: Write tree tests

Test the stack-based path reconstruction:

```python
class TestBuildPaths:
    def test_flat_entries(self):
        entries = [(0, "A"), (0, "B"), (0, "C")]
        assert list(build_paths(entries)) == ["A", "B", "C"]

    def test_nested_entries(self):
        entries = [(0, "Root"), (1, "Sub"), (2, "Deep")]
        assert list(build_paths(entries)) == ["Root", "Root/Sub", "Root/Sub/Deep"]

    def test_sibling_depth_reset(self):
        entries = [
            (0, "Root"), (1, "Sub1"), (2, "Deep1"),
            (1, "Sub2"), (2, "Deep2"),
        ]
        assert list(build_paths(entries)) == [
            "Root", "Root/Sub1", "Root/Sub1/Deep1",
            "Root/Sub2", "Root/Sub2/Deep2",
        ]

    def test_empty_input(self):
        assert list(build_paths(iter([]))) == []

    def test_depth_skips_back(self):
        entries = [(0, "A"), (1, "B"), (2, "C"), (0, "D")]
        assert list(build_paths(entries)) == ["A", "A/B", "A/B/C", "D"]
```

**Pitfall:** Test depth going backward (skipping levels) — this exercises the stack pop logic.

---

## Step 5: Write exporter tests

Test CSV and JSON output:

```python
class TestToCSV:
    def test_writes_header_and_rows(self, flat_catalog, tmp_path):
        out_path = tmp_path / "out.csv"
        to_csv(flat_catalog, out_path)
        content = out_path.read_text(encoding="utf-8")
        lines = content.strip().splitlines()
        assert lines[0] == ",".join(CSV_COLUMNS)
        assert len(lines) == len(flat_catalog.entries) + 1

    def test_no_blank_lines_on_windows(self, flat_catalog, tmp_path):
        """CSV uses newline='' so no \r\r on Windows."""
        out_path = tmp_path / "out.csv"
        to_csv(flat_catalog, out_path)
        content = out_path.read_bytes()
        assert b"\r\r" not in content

    def test_quotes_commas_in_names(self, tmp_path):
        from cdindex_parser.models import Entry
        from datetime import datetime


---

## Step 6: Write CLI tests

Test the CLI entry point directly (import-based, not subprocess):

```python
class TestBuildParser:
    def test_returns_argument_parser(self):
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_default_encoding_is_utf16(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk"])
        assert args.encoding == "utf-16"


class TestMain:
    def test_main_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_main_no_args_exits_two(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 2

    def test_main_missing_file_returns_one(self, tmp_path):
        result = main([str(tmp_path / "nonexistent"), "-o", str(tmp_path / "out.csv")])
        assert result == 1

    def test_main_end_to_end(self, sample_pair, tmp_path):
        idx_path, _ = sample_pair
        out_path = tmp_path / "out.csv"
        result = main([str(idx_path), "-o", str(out_path), "--encoding", "utf-8"])
        assert result == 0
        assert out_path.exists()
```

**Pitfall:** `argparse` calls `sys.exit()` via `SystemExit`. Wrap `main()` calls in `pytest.raises(SystemExit)` and assert `.code`.

**Pitfall:** `main()` returns an int exit code on success/error paths (not `SystemExit`). Test both.

---

## Step 7: Write error tests

Test the exception hierarchy:

```python
class TestExceptionHierarchy:
    def test_cdindex_error_is_exception(self):
        assert issubclass(CDIndexError, Exception)

    def test_line_count_mismatch_is_value_error(self):
        assert issubclass(LineCountMismatchError, ValueError)
        assert issubclass(LineCountMismatchError, CDIndexError)

    def test_malformed_record_has_line_number(self):
        exc = MalformedRecordError("bad line", line_number=42)
        assert exc.line_number == 42

    def test_errors_are_value_error_catchable(self):
        for exc_class in [LineCountMismatchError, IndentMismatchError, MalformedRecordError]:
            try:
                raise exc_class("test")
            except ValueError:
                pass
            else:
                pytest.fail(f"{exc_class.__name__} not catchable as ValueError")
```

**Pitfall:** `EncodingError` extends `UnicodeDecodeError` which needs 5 args in `__init__`. Test it separately with all 5 args, or don't subclass `UnicodeDecodeError`.

**Pitfall:** All errors should be catchable as both `CDIndexError` and `ValueError` (for backward compatibility).

---

## Step 8: Configure coverage gate

In `pyproject.toml`:

```toml
[tool.coverage.run]
branch = true
source = ["cdindex_parser"]

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:", "raise NotImplementedError"]
```

**Pitfall:** `branch = true` enables branch coverage (stricter than line coverage).

**Pitfall:** `fail_under = 80` fails the build if coverage drops below 80%.

---

## Step 9: Run and verify

```bash
pytest tests/ --cov=cdindex_parser --cov-branch --cov-report=term-missing
```

**Pass criteria:** All tests pass, coverage ≥ 80%.

**Interpretation:** Report coverage per module. Add tests for uncovered branches (error paths, edge cases, `-O` disabled asserts).

---
        catalog = Catalog(
            entries=(Entry(
                depth=0, name="\u96fb\u80fd\u6587\u4ef6.txt", is_dir=False,
                size_bytes=100, mtime=datetime(2023, 1, 1),
                path="\u96fb\u80fd\u6587\u4ef6.txt",
            ),)
        )
        out_path = tmp_path / "out.json"
        to_json(catalog, out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "\u96fb\u80fd\u6587\u4ef6" in content
```

**Pitfall:** CSV must use `newline=""` in `open()` to prevent `\r\r` on Windows.

**Pitfall:** JSON must use `ensure_ascii=False` to preserve non-ASCII (CJK) characters.

---
**Pitfall:** Test `resolve_input_path` with corruptible names (`MyID.IDX`, `GAME.IDX`) — this was the silent data-corruption bug.

---
                depth=0, name="File A.txt", is_dir=False,
                size_bytes=100, mtime=datetime(2023, 1, 1, 12, 0, 0),
                path="File A.txt",
            ),
            Entry(
                depth=0, name="File B.txt", is_dir=False,
                size_bytes=200, mtime=datetime(2023, 1, 1, 13, 0, 0),
                path="File B.txt",
            ),
        )
    )
```

**Pitfall:** Fixtures that create files must use `tmp_path` (automatic cleanup), not hardcoded paths.

**Pitfall:** Tab characters in test data must be actual `\t` characters, not spaces. Use `T = "\t"` constant.
