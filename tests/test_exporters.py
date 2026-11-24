"""Tests for cdindex2_parser.exporters — CSV and JSON export."""

import json

from cdindex2_parser.exporters import CSV_COLUMNS, iter_rows, to_csv, to_json
from cdindex2_parser.models import Catalog, Entry


class TestIterRows:
    """Tests for iter_rows — entry-to-dict conversion."""

    def test_csv_columns(self, flat_catalog: Catalog):
        rows = list(iter_rows(flat_catalog))
        assert len(rows) == len(flat_catalog.entries)
        for row in rows:
            assert set(row.keys()) == set(CSV_COLUMNS)

    def test_is_dir_values(self, flat_catalog: Catalog):
        rows = list(iter_rows(flat_catalog))
        for row, entry in zip(rows, flat_catalog.entries, strict=False):
            expected = "1" if entry.is_dir else "0"
            assert row["IsDir"] == expected

    def test_mtime_format(self, flat_catalog: Catalog):
        rows = list(iter_rows(flat_catalog))
        for row in rows:
            # Should match YYYY-MM-DDTHH:MM:SS
            assert len(row["MtimeStr"]) == 19
            assert row["MtimeStr"][4] == "-"
            assert row["MtimeStr"][10] == "T"


class TestToCSV:
    """Tests for to_csv."""

    def test_writes_header_and_rows(self, flat_catalog: Catalog, tmp_path):
        out_path = tmp_path / "out.csv"
        to_csv(flat_catalog, out_path)
        content = out_path.read_text(encoding="utf-8")
        lines = content.strip().splitlines()
        assert lines[0] == ",".join(CSV_COLUMNS)
        assert len(lines) == len(flat_catalog.entries) + 1

    def test_no_blank_lines_on_windows(self, flat_catalog: Catalog, tmp_path):
        """CSV uses newline='' so no \\r\\r on Windows."""
        out_path = tmp_path / "out.csv"
        to_csv(flat_catalog, out_path)
        content = out_path.read_bytes()
        assert b"\r\r" not in content

    def test_quotes_commas_in_names(self, tmp_path):
        catalog = Catalog(
            entries=(
                Entry(
                    depth=0,
                    name="File, with, commas.txt",
                    is_dir=False,
                    size_bytes=100,
                    mtime=__import__("datetime").datetime(2023, 1, 1),
                    path="Dir/File, with, commas.txt",
                ),
            )
        )
        out_path = tmp_path / "out.csv"
        to_csv(catalog, out_path)
        content = out_path.read_text(encoding="utf-8")
        assert '"Dir/File, with, commas.txt"' in content


class TestToJSON:
    """Tests for to_json."""

    def test_writes_version_and_entries(self, flat_catalog: Catalog, tmp_path):
        out_path = tmp_path / "out.json"
        to_json(flat_catalog, out_path)
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["version"] == 1
        assert "entries" in data
        assert len(data["entries"]) == len(flat_catalog.entries)

    def test_entry_fields(self, flat_catalog: Catalog, tmp_path):
        out_path = tmp_path / "out.json"
        to_json(flat_catalog, out_path)
        data = json.loads(out_path.read_text(encoding="utf-8"))
        entry = data["entries"][0]
        assert set(entry.keys()) == {"path", "is_dir", "size_bytes", "mtime"}

    def test_ensure_ascii_false(self, tmp_path):
        """Non-ASCII names should be written as-is, not escaped."""
        from datetime import datetime

        catalog = Catalog(
            entries=(
                Entry(
                    depth=0,
                    name="\u96fb\u80fd\u6587\u4ef6.txt",
                    is_dir=False,
                    size_bytes=100,
                    mtime=datetime(2023, 1, 1),
                    path="\u96fb\u80fd\u6587\u4ef6.txt",
                ),
            )
        )
        out_path = tmp_path / "out.json"
        to_json(catalog, out_path)
        content = out_path.read_text(encoding="utf-8")
        assert "\u96fb\u80fd\u6587\u4ef6" in content
