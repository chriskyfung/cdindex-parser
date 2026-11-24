# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-24

### Added

- Typed public API with frozen dataclasses (`Catalog`, `Entry`, `FileRecord`, `NameRecord`)
- `src/cdindex2_parser/` package layout with `py.typed` marker (PEP 561)
- `cdindex2-parser` console script with argparse CLI (`--encoding`, `--format`, `--version`)
- JSON export (`to_json`) alongside existing CSV export (`to_csv`)
- Configurable input encoding (UTF-16 default, Big5, CP950 supported)
- `resolve_input_path()` helper fixing silent name corruption bug
- `decode_dos_datetime()` utility for FAT timestamp decoding
- Comprehensive test suite (75 tests, 93% branch coverage)
- CI/CD pipeline: lint, Linux+Windows test matrix (3.10–3.14), build/smoke, CI gate
- Release workflow: TestPyPI → PyPI → GitHub Release via trusted publishing
- MkDocs Material documentation site with auto-generated API reference
- `.gitattributes`, `.pre-commit-config.yaml`, issue/PR templates

### Changed

- Migrated from root-level `decode_cdindex.py` script to `src/cdindex2_parser` package
- Replaced `dict` returns with typed dataclasses (`FileRecord`, `NameRecord`, `Entry`, `Catalog`)
- Replaced `assert` flow control with typed exceptions (`LineCountMismatchError`, `IndentMismatchError`, `MalformedRecordError`)
- Renamed CLI from `decode_cdindex.py` to `cdindex2-parser`
- Renamed console script entry point from `scripts.decode_cdindex` to `cdindex2_parser.cli:main`
- Bumped minimum Python to 3.10
- Switched license metadata to PEP 639 SPDX form (`license = "MIT"` + `license-files`)

### Fixed

- `resolve_input_path()` no longer corrupts names like `MyID.IDX` → `My` (was `str.rstrip()` character-set bug)
- Case-insensitive `.IDX`/`.FILE` suffix matching
- Dotted base names (e.g. `archive.1.IDX`) no longer truncated by `Path.with_suffix()`
- `__main__` entry point guarded with `if __name__ == "__main__":`

### Removed

- Root-level `decode_cdindex.py` script (replaced by package)

## [0.2.1] - 2026-11-23

### Added

- Added `.gitattributes` to normalize line endings and mark binary files
- Added `.pre-commit-config.yaml` with pre-commit hooks for linting and formatting

### Changed

- Updated `.gitignore` to exclude distribution/build artifacts and preserve test fixtures

### Fixed

- Fixed `resolve_input_path` to correctly strip `.IDX`/`.FILE` suffixes instead of using `rstrip` as a character set, preventing corruption of filenames like `MyID.IDX`

## [0.2.0] - 2026-11-22

### Added

- Initial parser for CD Index 2 `.IDX` and `.FILE` files
- Line-by-line structure matching algorithm
- CSV/JSON export with full path reconstruction
- Big5 encoding support for Traditional Chinese
- Stack-based directory tree reconstruction

### Changed

- Updated return type of `parse_file_line` and `parse_name_line` to consistent dict literals
- Switched `startswith` check to tuple syntax for cleaner condition
- Updated assertion error message to use f-string formatting

### Fixed

- N/A

## [0.1.0] - 2026-03-17

### Added

- Complete Python parser implementation
- Unix timestamp → ISO-8601 conversion
- Indentation-based depth calculation
- README.md with full documentation
- Error handling for encoding mismatches

### Changed

- Initial release - first functional version

### Fixed

- Proper handling of directory (D) vs file (F) type prefixes
- Robust line count validation between IDX/FILE pairs
