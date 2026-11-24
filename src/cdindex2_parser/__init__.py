"""Public API for cdindex2-parser."""

from importlib.metadata import PackageNotFoundError, version

from .exporters import to_csv, to_json
from .models import Catalog, Entry, FileRecord, NameRecord
from .parser import parse_catalog, parse_file_line, parse_name_line, resolve_input_path

try:
    __version__ = version("cdindex2-parser")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "Catalog",
    "Entry",
    "FileRecord",
    "NameRecord",
    "__version__",
    "parse_catalog",
    "parse_file_line",
    "parse_name_line",
    "resolve_input_path",
    "to_csv",
    "to_json",
]
