"""Pytest fixtures for cdindex-parser tests."""

from pathlib import Path

import pytest

from cdindex_parser.models import Catalog, Entry

T = "\t"


def write_pair(
    tmp_path: Path,
    base: str,
    idx_content: str,
    file_content: str,
    encoding: str = "utf-8",
) -> tuple[Path, Path]:
    """Write a .IDX/.FILE pair and return their paths."""
    idx_path = tmp_path / f"{base}.IDX"
    file_path = tmp_path / f"{base}.FILE"
    idx_path.write_text(idx_content, encoding=encoding)
    file_path.write_text(file_content, encoding=encoding)
    return idx_path, file_path


@pytest.fixture
def sample_pair(tmp_path: Path) -> tuple[Path, Path]:
    """A simple .IDX/.FILE pair with nested directory structure."""
    idx_content = (
        "Root Folder\n"
        + T
        + "File 1-1.txt\n"
        + T
        + "File 1-2.txt\n"
        + T
        + "Sub Folder\n"
        + T
        + T
        + "File 2-1.txt\n"
    )
    file_content = (
        "D0.25482084\n"
        + T
        + "F226.25482084\n"
        + T
        + "F528.25482084\n"
        + T
        + "D0.25482084\n"
        + T
        + T
        + "F100.25482084\n"
    )
    return write_pair(tmp_path, "sample", idx_content, file_content)


@pytest.fixture
def flat_pair(tmp_path: Path) -> tuple[Path, Path]:
    """A flat .IDX/.FILE pair (no nesting)."""
    idx_content = "File A.txt\nFile B.txt\n"
    file_content = "F100.25482084\nF200.25482084\n"
    return write_pair(tmp_path, "flat", idx_content, file_content)


@pytest.fixture
def utf16_pair(tmp_path: Path) -> tuple[Path, Path]:
    """A .IDX/.FILE pair encoded as UTF-16 with BOM."""
    idx_content = "Root Folder\n\tFile.txt\n"
    file_content = "D0.25482084\n\tF100.25482084\n"
    return write_pair(tmp_path, "utf16", idx_content, file_content, encoding="utf-16")


@pytest.fixture
def big5_pair(tmp_path: Path) -> tuple[Path, Path]:
    """A .IDX/.FILE pair encoded as Big5 (Traditional Chinese)."""
    idx_content = "Root Folder\n\t\u96fb\u80fd\u6587\u4ef6.txt\n"
    file_content = "D0.25482084\n\tF100.25482084\n"
    return write_pair(tmp_path, "big5", idx_content, file_content, encoding="big5")


@pytest.fixture
def flat_catalog() -> Catalog:
    """A simple Catalog with two entries for exporter tests."""
    from datetime import datetime

    return Catalog(
        entries=(
            Entry(
                depth=0,
                name="File A.txt",
                is_dir=False,
                size_bytes=100,
                mtime=datetime(2023, 1, 1, 12, 0, 0),
                path="File A.txt",
            ),
            Entry(
                depth=0,
                name="File B.txt",
                is_dir=False,
                size_bytes=200,
                mtime=datetime(2023, 1, 1, 13, 0, 0),
                path="File B.txt",
            ),
        )
    )
