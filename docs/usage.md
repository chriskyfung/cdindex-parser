# Usage Guide

`cdindex-parser` can be used as a command-line tool or as a Python library.

## Command-Line Interface (CLI)

The primary script for parsing is `decode_cdindex.py`.

### Basic Parsing

To parse a pair of `cdindex` files (`.IDX` and `.FILE`) into a CSV file, you need to provide the base name of the input files (without extension) and the desired output CSV file path.

For example, if you have `mydisk.IDX` and `mydisk.FILE` in the same directory, you would run:

```bash
python decode_cdindex.py mydisk results.csv
```

The script will look for `mydisk.IDX` and `mydisk.FILE`, process them, and save the output to `results.csv`.

**Output CSV columns**:

- `FullPath`: The full path of the file or directory.
- `IsDir`: `1` if it's a directory, `0` if it's a file.
- `SizeBytes`: The size of the file in bytes (0 for directories).
- `MtimeStr`: The modification time in `YYYY-MM-DDTHH:MM:SS` format.
