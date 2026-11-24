# CD Index 2 Parser

[![codecov](https://codecov.io/gh/chriskyfung/cdindex2-parser/graph/badge.svg?token=AHQ1APGM2W)](https://codecov.io/gh/chriskyfung/cdindex2-parser)
[![CI](https://github.com/chriskyfung/cdindex2-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/chriskyfung/cdindex2-parser/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cdindex2-parser)](https://pypi.org/project/cdindex2-parser/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cdindex2-parser)](https://pypi.org/project/cdindex2-parser/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/chriskyfung/cdindex2-parser/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/chriskyfung/cdindex2-parser)

**CD Index 2 Parser** converts legacy `*.IDX` and `*.FILE` files from CD Index 2 (光碟索引大師) into modern CSV/JSON formats, preserving the full file tree structure, sizes, and modification timestamps.

This tool is for anyone who has old CD/DVD index catalogs from this popular legacy software and wants to access them with modern tools.

**📖 Full Documentation: https://chriskyfung.github.io/cdindex2-parser/**

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
pip install cdindex2-parser
```

Parse a pair of `.IDX`/`.FILE` files into CSV:

```bash
cdindex2-parser mydisk results.csv
```

Or parse into JSON:

```bash
cdindex2-parser mydisk results.json --format json
```

Use it as a Python library:

```python
from cdindex2_parser import parse_catalog

catalog = parse_catalog("mydisk.IDX", encoding="utf-16")
for entry in catalog:
    print(f"{entry.path}  is_dir={entry.is_dir}  size={entry.size_bytes}")
```

---

## 📖 Documentation

| Document | Link |
|---|---|
| Installation | [Docs › Installation](https://chriskyfung.github.io/cdindex2-parser/installation/) |
| Usage | [Docs › Usage](https://chriskyfung.github.io/cdindex2-parser/usage/) |
| File Format | [Docs › File Format](https://chriskyfung.github.io/cdindex2-parser/file-format/) |
| API Reference | [Docs › API Reference](https://chriskyfung.github.io/cdindex2-parser/api/) |
| Troubleshooting | [Docs › Troubleshooting](https://chriskyfung.github.io/cdindex2-parser/troubleshooting/) |

---

## License

MIT License. See [LICENSE](https://github.com/chriskyfung/cdindex2-parser/blob/main/LICENSE) for details.
