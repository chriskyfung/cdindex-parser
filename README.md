# CD Index 2 Parser

**CD Index 2 Parser** converts legacy `*.IDX` (file tree) and `*.FILE` (properties) files from CD Index 2 (光碟索引大師) into modern CSV/JSON formats with full file properties including size, modification timestamps, and directory structure.

## Features

- Parses tab-indented tree structures from `.IDX` files
- Decodes `D<size>.<timestamp>` and `F<size>.<timestamp>` format from `.FILE` files
- Converts Unix timestamps to human-readable ISO-8601 dates
- Reconstructs full file paths from indentation levels
- Handles Big5/Traditional Chinese encoding
- Outputs CSV, JSON, or directory tree visualization

## File Format

### `*.IDX` (Names & Structure)

```plaintext
Root Folder
    File 1-1.txt
    File 1-2.txt
    Sub Folder 1
        File 2-1.txt
```

### `*.FILE` (Properties)

```plaintext
D0.1334278694        # Directory, size 0, timestamp 1334278694
    F226.1334278694  # File, 226 bytes, timestamp 1334278694
    F528.1334278694
    D0.1334278728
        F247888.1334278734  # 247KB file, 2019-12-07T15:18:28
```

## Installation

```bash
pip install cdindex-parser
```

Or save the script locally:

```bash
git clone <this-repo>
cd cdindex-parser
pip install -r requirements.txt
```

**Requirements**: Python 3.6+, `pandas` (optional for CSV export)

## Quick Start

```bash
# Parse single index pair
python decode_cdindex.py disk1.IDX disk1.FILE output.csv

# Batch process all indexes in directory
python batch_parse.py /path/to/indexes/

# Generate directory tree visualization
python decode_cdindex.py disk1.IDX disk1.FILE --tree tree.png
```

**Input**: Paired `*.IDX` + `*.FILE` files (same base name)
**Output**: CSV with columns `FullPath,IsDir,SizeBytes,MtimeStr`

## Usage Examples

### Basic Parsing

```bash
python decode_cdindex.py mydisk.IDX mydisk.FILE results.csv
```

**Output CSV**:

```csv
FullPath,IsDir,SizeBytes,MtimeStr
Root/,1,0,2012-04-07T12:34:54
Root/file1.txt,0,247888,2019-12-07T15:18:28
Root/subdir/,1,0,2012-04-07T12:35:02
Root/subdir/doc.pdf,0,528492,2019-12-08T09:22:17
```

### Advanced Options

```bash
python decode_cdindex.py disk1.IDX disk1.FILE \
    --output json:disk1.json \
    --output tree:tree.html \
    --encoding big5 \
    --tz Asia/Hong_Kong
```

## API Usage

```python
from cdindex_parser import parse_cdindex_pair

idx_path = "disk1.IDX"
file_path = "disk1.FILE"

records = parse_cdindex_pair(idx_path, file_path, encoding='big5')

# Convert to pandas DataFrame
df = pd.DataFrame(records)
df.to_csv('output.csv', index=False)

# Filter large files only
large_files = [r for r in records if r['size_bytes'] > 10**6]
```

## Output Formats

| Format | Command                   | Description                           |
| ------ | ------------------------- | ------------------------------------- |
| CSV    | `--output csv:file.csv`   | Spreadsheet-ready with full paths     |
| JSON   | `--output json:file.json` | Structured data for other tools       |
| Tree   | `--output tree:tree.html` | Interactive directory visualization   |
| Stats  | `--stats`                 | Summary: total files, size, age range |

## Troubleshooting

### Encoding Issues

```shell:outupt
Error: Garbled Chinese characters
```

**Fix**: Use `--encoding big5` or `--encoding cp950`

### Line Count Mismatch

```shell:outupt
Error: IDX has 1250 lines, FILE has 1249 lines
```

**Fix**: Files may be corrupted. Use `--tolerant` to skip mismatches.

### Wrong Timestamps

```shell:outupt
2012 instead of 2019?
```

**Fix**: Timestamps are Unix seconds. Verify with `date -d @1334278734`

## Structure Recovery Algorithm

1. **Line-by-line pairing**: Nth line of `.IDX` ↔ Nth line of `.FILE`
2. **Indentation matching**: Tab count determines depth
3. **Path reconstruction**: Stack-based path building from root
4. **Timestamp conversion**: Unix epoch → ISO-8601
5. **Size parsing**: Extract digits before `.` in `Fnnn.tttttt`

```shell:outupt
Line 1: "Root Folder"     ↔ "D0.1334278694"
Line 2: "    File1.txt"   ↔ "F247888.1334278734"
Line 3: "    Subdir/"     ↔ "D0.1334278728"
```

## Limitations

- Assumes perfect line correspondence between `.IDX` and `.FILE`
- No support for multi-volume indexes
- Timestamps are Unix epoch (no timezone in source)
- No CRC/hash validation

## Development

```bash
# Run tests
pytest tests/

# Format
ruff format .

# Lint
ruff check .

# Build
python -m build
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Based on reverse engineering of CD Index 2 (光碟索引大師) format
- Thanks to original CD Index developers for the pure-text database design

***

**⭐ Found this helpful?** Share your parsed CD collections!  
**🐛 Bug?** Open an issue with sample `.IDX`/`.FILE` lines (sanitized).
