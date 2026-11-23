"""Tests for cdindex_parser.parser — parsing logic and input-path resolution."""

from datetime import datetime
from pathlib import Path

import pytest

from cdindex_parser.errors import (
    IndentMismatchError,
    InputNotFoundError,
    LineCountMismatchError,
    MalformedRecordError,
)
from cdindex_parser.parser import (
    decode_dos_datetime,
    match_and_dump,
    parse_catalog,
    parse_file_line,
    parse_name_line,
    resolve_input_path,
)


class TestResolveInputPath:
    """Tests for resolve_input_path — the fix for the rstrip corruption bug."""

    def test_base_name(self):
        idx, file = resolve_input_path("mydisk")
        assert idx == "mydisk.IDX"
        assert file == "mydisk.FILE"

    def test_with_idx_suffix(self):
        idx, file = resolve_input_path("mydisk.IDX")
        assert idx == "mydisk.IDX"
        assert file == "mydisk.FILE"

    def test_with_file_suffix(self):
        idx, file = resolve_input_path("mydisk.FILE")
        assert idx == "mydisk.IDX"
        assert file == "mydisk.FILE"

    def test_preserves_corruptible_names(self):
        """The old rstrip() corrupted MyID.IDX→My and GAME.IDX→GAM."""
        for p in ["MyID.IDX", "GAME.IDX", "DISK.IDX", "ARCHIVE.IDX"]:
            idx, file = resolve_input_path(p)
            assert idx == p
            assert file == p[:-4] + ".FILE"

    def test_lowercase_suffix(self):
        idx, file = resolve_input_path("mydisk.idx")
        assert idx == "mydisk.IDX"
        assert file == "mydisk.FILE"

    def test_with_directory(self):
        idx, file = resolve_input_path("/home/user/data.mydisk.IDX")
        assert idx == "/home/user/data.mydisk.IDX"
        assert file == "/home/user/data.mydisk.FILE"

    def test_dotted_base_name(self):
        idx, file = resolve_input_path("archive.1.IDX")
        assert idx == "archive.1.IDX"
        assert file == "archive.1.FILE"


class TestParseFileLine:
    """Tests for parse_file_line — .FILE line parsing."""

    def test_directory_record(self):
        record = parse_file_line("D0.25482084")
        assert record.indent == 0
        assert record.type == "D"
        assert record.size == 0
        assert record.ts == 25482084

    def test_file_record(self):
        record = parse_file_line("F226.25482084")
        assert record.indent == 0
        assert record.type == "F"
        assert record.size == 226
        assert record.ts == 25482084

    def test_indent_detection(self):
        record = parse_file_line("\tF226.25482084")
        assert record.indent == 1

    def test_negative_timestamp(self):
        record = parse_file_line("D0.-1")
        assert record.size == 0
        assert record.ts == -1

    def test_malformed_no_dot(self):
        with pytest.raises(MalformedRecordError) as exc:
            parse_file_line("D25482084")
        assert exc.value.line_number is None

    def test_not_d_or_f(self):
        with pytest.raises(MalformedRecordError):
            parse_file_line("X0.25482084")


class TestParseNameLine:
    """Tests for parse_name_line — .IDX line parsing."""

    def test_root_level(self):
        record = parse_name_line("Root Folder")
        assert record.indent == 0
        assert record.name == "Root Folder"

    def test_indented(self):
        record = parse_name_line("\tFile.txt")
        assert record.indent == 1
        assert record.name == "File.txt"

    def test_deep_indent(self):
        record = parse_name_line("\t\t\tDeep.txt")
        assert record.indent == 3
        assert record.name == "Deep.txt"

    def test_trailing_newline_stripped(self):
        record = parse_name_line("File.txt\n")
        assert record.name == "File.txt"


class TestDecodeDOSDatetime:
    """Tests for decode_dos_datetime — FAT timestamp decoding."""

    def test_known_timestamp(self):
        # 1130591439 -> 2013-11-03 14:38:30
        dt = decode_dos_datetime(1130591439)
        assert dt == datetime(2013, 11, 3, 14, 38, 30)

    def test_negative_timestamp(self):
        assert decode_dos_datetime(-1) == datetime(1970, 1, 1)

    def test_invalid_date(self):
        # month=13 → invalid → epoch
        dos_date = (13 << 5) | 1  # month=13, day=1
        dos_time = 0
        ts = (dos_date << 16) | dos_time
        assert decode_dos_datetime(ts) == datetime(1970, 1, 1)


class TestParseCatalog:
    """End-to-end tests for parse_catalog."""

    def test_flat_pair(self, flat_pair: tuple[Path, Path]):
        idx_path, _ = flat_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        assert len(catalog) == 2
        assert catalog.entries[0].name == "File A.txt"
        assert catalog.entries[0].is_dir is False
        assert catalog.entries[0].size_bytes == 100
        assert catalog.entries[1].name == "File B.txt"
        assert catalog.entries[1].is_dir is False
        assert catalog.entries[1].size_bytes == 200

    def test_nested_structure(self, sample_pair: tuple[Path, Path]):
        idx_path, _ = sample_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        assert len(catalog) == 5

        # Check paths are reconstructed correctly
        paths = [e.path for e in catalog]
        assert "Root Folder" in paths
        assert "Root Folder/File 1-1.txt" in paths
        assert "Root Folder/File 1-2.txt" in paths
        assert "Root Folder/Sub Folder" in paths
        assert "Root Folder/Sub Folder/File 2-1.txt" in paths

    def test_depth_values(self, sample_pair: tuple[Path, Path]):
        idx_path, _ = sample_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        depths = [e.depth for e in catalog]
        assert depths == [0, 1, 1, 1, 2]

    def test_utf16_encoding(self, utf16_pair: tuple[Path, Path]):
        idx_path, _ = utf16_pair
        catalog = parse_catalog(idx_path, encoding="utf-16")
        assert len(catalog) == 2
        assert catalog.entries[1].name == "File.txt"

    def test_big5_encoding(self, big5_pair: tuple[Path, Path]):
        idx_path, _ = big5_pair
        catalog = parse_catalog(idx_path, encoding="big5")
        assert len(catalog) == 2
        assert "\u96fb\u80fd\u6587\u4ef6" in catalog.entries[1].name

    def test_input_path_accepted(self, sample_pair: tuple[Path, Path]):
        idx_path, _ = sample_pair
        # Passing just the base path (without extension) should work
        base = str(idx_path.with_suffix(""))
        catalog = parse_catalog(base, encoding="utf-8")
        assert len(catalog) == 5

    def test_line_count_mismatch(self, tmp_path: Path):
        (tmp_path / "bad.IDX").write_text("A\nB\n", encoding="utf-8")
        (tmp_path / "bad.FILE").write_text("D0.25482084\n", encoding="utf-8")
        with pytest.raises(LineCountMismatchError):
            parse_catalog(tmp_path / "bad", encoding="utf-8")

    def test_missing_file(self, tmp_path: Path):
        with pytest.raises(InputNotFoundError):
            parse_catalog(tmp_path / "nonexistent", encoding="utf-8")

    def test_match_and_dump_writes_csv(
        self, sample_pair: tuple[Path, Path], tmp_path: Path
    ):
        idx_path, _ = sample_pair
        out_path = tmp_path / "out.csv"
        match_and_dump(idx_path, out_path, encoding="utf-8")
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        assert "FullPath,IsDir,SizeBytes,MtimeStr" in content
        assert "Root Folder" in content

    def test_idx_file_missing(self, tmp_path: Path):
        """IDX missing should raise InputNotFoundError (covers except branch)."""
        (tmp_path / "only.FILE").write_text("D0.25482084\n", encoding="utf-8")
        with pytest.raises(InputNotFoundError):
            parse_catalog(tmp_path / "only", encoding="utf-8")

    def test_malformed_file_line_in_catalog(self, tmp_path: Path):
        """Malformed .FILE line inside parse_catalog triggers re-raise."""
        (tmp_path / "bad.IDX").write_text("A\n", encoding="utf-8")
        (tmp_path / "bad.FILE").write_text("not-a-valid-line\n", encoding="utf-8")
        with pytest.raises(MalformedRecordError) as exc:
            parse_catalog(tmp_path / "bad", encoding="utf-8")
        assert exc.value.line_number == 1

    def test_indent_mismatch_in_catalog(self, tmp_path: Path):
        """Indent mismatch between .IDX and .FILE lines."""
        (tmp_path / "bad.IDX").write_text("A\n\tB\n", encoding="utf-8")
        (tmp_path / "bad.FILE").write_text(
            "D0.25482084\nD0.25482084\n", encoding="utf-8"
        )
        with pytest.raises(IndentMismatchError):
            parse_catalog(tmp_path / "bad", encoding="utf-8")


class TestCatalog:
    """Tests for the Catalog container."""

    def test_iteration(self, flat_pair: tuple[Path, Path]):
        idx_path, _ = flat_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        entries = list(catalog)
        assert len(entries) == 2
        assert all(hasattr(e, "path") for e in entries)

    def test_len(self, flat_pair: tuple[Path, Path]):
        idx_path, _ = flat_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        assert len(catalog) == 2

    def test_entries_are_immutable(self, flat_pair: tuple[Path, Path]):
        idx_path, _ = flat_pair
        catalog = parse_catalog(idx_path, encoding="utf-8")
        with pytest.raises(AttributeError):
            catalog.entries.append(object())  # type: ignore[attr-defined]
