# Usage Guide

`cdindex-parser` can be used as a command-line tool or as a Python library.

## Command-Line Interface (CLI)

The `cdindex-parser` command is installed automatically when you install the package.

### Basic Parsing

To parse a pair of `.IDX`/`.FILE` files into a CSV file, provide the base name of the input files:

```bash
cdindex-parser mydisk results.csv
```

This looks for `mydisk.IDX` and `mydisk.FILE`, processes them, and writes `results.csv`.

You can also pass the `.IDX` path directly:

```bash
cdindex-parser mydisk.IDX results.csv
```

### CLI Options

| Option | Description | Default |
|---|---|---|
| `input` | Base name or path of the `.IDX`/`.FILE` pair | (required) |
| `-o`, `--output` | Output file path | `<input>.csv` |
| `--format` | Output format: `csv` or `json` | Inferred from output suffix |
| `--encoding` | Input text encoding | `utf-16` |
| `--version` | Show version and exit | — |

### Examples

Parse to CSV (format inferred from `.csv` suffix):

```bash
cdindex-parser mydisk results.csv
```

Parse to JSON:

```bash
cdindex-parser mydisk results.json --format json
```

Use a non-default encoding (e.g. Big5 for Traditional Chinese names):

```bash
cdindex-parser mydisk results.csv --encoding big5
```

### Output Format

**CSV** output columns:

| Column | Description |
|---|---|
| `FullPath` | Full path reconstructed from the indented tree |
| `IsDir` | `1` if directory, `0` if file |
| `SizeBytes` | File size in bytes (`0` for directories) |
| `MtimeStr` | Modification time (`YYYY-MM-DDTHH:MM:SS`) |

**JSON** output schema (version 1):

```json
{
  "version": 1,
  "entries": [
    {
      "path": "Root Folder/File.txt",
      "is_dir": false,
      "size_bytes": 226,
      "mtime": "2013-11-03T14:38:30"
    }
  ]
}
```

## Python Library

Import and use the typed API directly:

```python
from cdindex_parser import parse_catalog, Catalog

# Parse an IDX/FILE pair
catalog: Catalog = parse_catalog("mydisk.IDX", encoding="utf-16")

# Iterate over entries
for entry in catalog:
    print(
        f"{entry.path}  "
        f"is_dir={entry.is_dir}  "
        f"size={entry.size_bytes}  "
        f"mtime={entry.mtime.isoformat()}"
    )
```

### Public API

| Symbol | Description |
|---|---|
| `parse_catalog(input_path, *, encoding)` | Parse an `.IDX`/`.FILE` pair into a `Catalog` |
| `Catalog` | Frozen dataclass holding `entries` (tuple of `Entry`) |
| `Entry` | A single parsed entry with `path`, `name`, `is_dir`, `size_bytes`, `mtime`, `depth` |
| `FileRecord` | Raw `.FILE` line record (`indent`, `type`, `size`, `ts`, `mtime`) |
| `NameRecord` | Raw `.IDX` line record (`indent`, `name`) |
| `resolve_input_path(input_path)` | Resolve base/suffixed path to `(.IDX, .FILE)` paths |
| `decode_dos_datetime(ts)` | Decode a 32-bit DOS FAT timestamp to `datetime` |
| `to_csv(catalog, out)` | Write a `Catalog` to CSV |
| `to_json(catalog, out)` | Write a `Catalog` to JSON |

See the [API Reference](api.md) for full details.
