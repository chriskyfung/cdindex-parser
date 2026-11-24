"""CSV and JSON exporters for cdindex2-parser catalogs."""

import csv
import json
from collections.abc import Iterator
from pathlib import Path

from .models import Catalog

CSV_COLUMNS = ("FullPath", "IsDir", "SizeBytes", "MtimeStr")


def iter_rows(catalog: Catalog) -> Iterator[dict[str, object]]:
    """Yield each ``Entry`` as a dict with CSV-column keys.

    The ``mtime`` is formatted as an ISO-8601-compatible string
    ``YYYY-MM-DDTHH:MM:SS``.
    """
    for entry in catalog:
        mtime_str = entry.mtime.strftime("%Y-%m-%dT%H:%M:%S")
        yield {
            "FullPath": entry.path,
            "IsDir": "1" if entry.is_dir else "0",
            "SizeBytes": entry.size_bytes,
            "MtimeStr": mtime_str,
        }


def to_csv(catalog: Catalog, out: str | Path) -> None:
    """Write a ``Catalog`` to CSV format.

    The output uses ``newline=""`` (as recommended for ``csv.writer`` on
    Windows) and ``csv.QUOTE_MINIMAL`` quoting.
    """
    out_path = Path(out)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CSV_COLUMNS)
        for row in iter_rows(catalog):
            writer.writerow([row[c] for c in CSV_COLUMNS])


def to_json(catalog: Catalog, out: str | Path) -> None:
    """Write a ``Catalog`` to JSON format.

    Output schema version 1:

    .. code-block:: json

        {
          "version": 1,
          "entries": [
            {
              "path": "dir/file.txt",
              "is_dir": false,
              "size_bytes": 226,
              "mtime": "2013-11-03T14:38:30"
            }
          ]
        }
    """
    out_path = Path(out)
    entries_data = [
        {
            "path": entry.path,
            "is_dir": entry.is_dir,
            "size_bytes": entry.size_bytes,
            "mtime": entry.mtime.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        for entry in catalog
    ]
    data = {"version": 1, "entries": entries_data}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
