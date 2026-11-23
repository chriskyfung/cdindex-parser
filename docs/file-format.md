# CD Index File Format

The CD Index 2 software uses a pair of files with the same base name to store the index: `*.IDX` and `*.FILE`.

## `*.IDX` (Names & Structure)

This file contains the names of files and directories, with their hierarchy represented by **tab indentation**. Each line corresponds to one entry in the `.FILE` file at the same line number.

**Example** (shown with `→` representing a tab):

```
Root Folder
→File 1-1.txt
→File 1-2.txt
→Sub Folder 1
→→File 2-1.txt
```

## `*.FILE` (Properties)

This file stores properties for each corresponding line in the `.IDX` file. Each line follows the format `[D|F]<size>.<timestamp>`.

| Component | Meaning |
|---|---|
| `D` | Directory |
| `F` | File |
| `<size>` | Size in bytes (`0` for directories) |
| `<timestamp>` | 32-bit MS-DOS FAT timestamp |

**Example** (shown with `→` representing a tab):

```
D0.1334278694
→F226.1334278694
→F528.1334278694
```

## Encoding

The `.IDX` and `.FILE` files are text files encoded in a legacy codepage. Common encodings include:

- **UTF-16** (default, with or without BOM)
- **Big5** / **CP950** (Traditional Chinese)
- **CP437** (US MS-DOS)

Select the encoding with the `--encoding` CLI option or the `encoding` parameter of `parse_catalog()`.

## Timestamp Format

The timestamp is a 32-bit integer in the **MS-DOS FAT timestamp** format (`dosdate`). This format stores the date and time as bit fields, relative to an epoch of **1980-01-01**.

The 32-bit integer is composed of two 16-bit parts:

- **Time** (lower 16 bits)
- **Date** (upper 16 bits)

### Decoding the Timestamp

Here is how the date and time components are extracted from the integer:

```python
# ts is the 32-bit integer timestamp
dos_time = ts & 0xFFFF
dos_date = ts >> 16

# Time decoding
sec = (dos_time & 0x1F) * 2  # 5 bits for seconds (in 2-second intervals)
minute = (dos_time >> 5) & 0x3F  # 6 bits for minutes
hour = dos_time >> 11  # 5 bits for hours

# Date decoding
day = dos_date & 0x1F  # 5 bits for day
month = (dos_date >> 5) & 0xF  # 4 bits for month
year = (dos_date >> 9) + 1980  # 7 bits for year (offset from 1980)
```

For example, the timestamp `1130591439` is decoded as `2013-11-03 14:38:30`.

## Line Correspondence

The `.IDX` and `.FILE` files must have the same number of non-empty lines. Line *n* in `.IDX` corresponds to line *n* in `.FILE`. A mismatch raises `LineCountMismatchError`.
