"""Tests for cdindex_parser.cli — command-line interface."""

import argparse
from pathlib import Path

import pytest

from cdindex_parser.cli import build_parser, main


class TestBuildParser:
    """Direct tests for build_parser (import-based, covers cli.py)."""

    def test_returns_argument_parser(self):
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_has_input_argument(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk"])
        assert args.input == "mydisk"

    def test_has_output_option(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk", "-o", "out.csv"])
        assert args.output == "out.csv"

    def test_has_format_option(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk", "--format", "json"])
        assert args.format == "json"

    def test_has_encoding_option(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk", "--encoding", "big5"])
        assert args.encoding == "big5"

    def test_default_encoding_is_utf16(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk"])
        assert args.encoding == "utf-16"

    def test_default_format_is_none(self):
        parser = build_parser()
        args = parser.parse_args(["mydisk"])
        assert args.format is None


class TestMain:
    """Direct tests for main() (import-based, covers cli.py)."""

    def test_main_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_main_no_args_exits_two(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 2

    def test_main_version_exits_zero(self):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0

    def test_main_missing_file_returns_one(self, tmp_path: Path):
        result = main([str(tmp_path / "nonexistent"), "-o", str(tmp_path / "out.csv")])
        assert result == 1

    def test_main_end_to_end(self, sample_pair: tuple[Path, Path], tmp_path: Path):
        idx_path, _ = sample_pair
        out_path = tmp_path / "out.csv"
        result = main([str(idx_path), "-o", str(out_path), "--encoding", "utf-8"])
        assert result == 0
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        assert "FullPath,IsDir,SizeBytes,MtimeStr" in content


class TestMainModule:
    """Tests for __main__.py module entry point."""

    def test_main_module_has_main(self):
        from cdindex_parser import __main__

        assert hasattr(__main__, "main")
        assert callable(__main__.main)
