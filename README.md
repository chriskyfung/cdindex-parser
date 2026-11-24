# CD Index 2 Parser

[![codecov](https://codecov.io/gh/chriskyfung/cdindex-parser/graph/badge.svg?token=AHQ1APGM2W)](https://codecov.io/gh/chriskyfung/cdindex-parser)
[![CI](https://github.com/chriskyfung/cdindex-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/chriskyfung/cdindex-parser/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cdindex-parser)](https://pypi.org/project/cdindex-parser/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cdindex-parser)](https://pypi.org/project/cdindex-parser/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/chriskyfung/cdindex-parser/blob/main/LICENSE)

**CD Index 2 Parser** converts legacy `*.IDX` and `*.FILE` files from CD Index 2 (光碟索引大師) into modern CSV/JSON formats, preserving the full file tree structure, sizes, and modification timestamps.

This tool is for anyone who has old CD/DVD index catalogs from this popular legacy software and wants to access them with modern tools.

**📖 Full Documentation: https://chriskyfung.github.io/cdindex-parser/**

---

## Features

- Parses file and directory structures from `.IDX` and `.FILE` pairs
- Correctly decodes the 32-bit MS-DOS FAT timestamps
- Reconstructs full file paths from tab-indented tree structures
- Outputs clean CSV or JSON
- Supports encodings like UTF-16, Big5, and CP950 for Traditional Chinese file names
- Zero runtime dependencies — pure Python standard library
- Typed API with frozen dataclasses — importable as a library

---

## Quick Start

Install from PyPI:

```bash
pip install cdindex-parser
```

Parse a pair of `.IDX`/`.FILE` files into CSV:

```bash
cdindex-parser mydisk results.csv
```

Or parse into JSON:

```bash
cdindex-parser mydisk results.json --format json
```

Use it as a Python library:

```python
from cdindex_parser import parse_catalog

catalog = parse_catalog("mydisk.IDX", encoding="utf-16")
for entry in catalog:
    print(f"{entry.path}  is_dir={entry.is_dir}  size={entry.size_bytes}")
```

---

## 📖 Documentation

| Document | Link |
|---|---|
| Installation | [Docs › Installation](https://chriskyfung.github.io/cdindex-parser/installation.html) |
| Usage | [Docs › Usage](https://chriskyfung.github.io/cdindex-parser/usage.html) |
| File Format | [Docs › File Format](https://chriskyfung.github.io/cdindex-parser/file-format.html) |
| API Reference | [Docs › API Reference](https://chriskyfung.github.io/cdindex-parser/api.html) |
| Troubleshooting | [Docs › Troubleshooting](https://chriskyfung.github.io/cdindex-parser/troubleshooting.html) |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
