"""Data models for cdindex-parser catalogs."""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime

FILE_TYPE_DIR = "D"
FILE_TYPE_FILE = "F"


@dataclass(frozen=True, slots=True)
class FileRecord:
    """A single record from a ``.FILE`` line."""

    indent: int
    type: str  # "D" | "F"
    size: int
    ts: int
    mtime: datetime


@dataclass(frozen=True, slots=True)
class NameRecord:
    """A single record from a ``.IDX`` line."""

    indent: int
    name: str


@dataclass(frozen=True, slots=True)
class Entry:
    """A resolved catalog entry with full path."""

    depth: int
    name: str
    is_dir: bool
    size_bytes: int
    mtime: datetime
    path: str


@dataclass(frozen=True, slots=True)
class Catalog:
    """A collection of resolved catalog entries."""

    entries: tuple[Entry, ...]

    def __iter__(self) -> Iterator[Entry]:
        """Iterate over the catalog entries."""
        return iter(self.entries)

    def __len__(self) -> int:
        """Return the number of entries."""
        return len(self.entries)
