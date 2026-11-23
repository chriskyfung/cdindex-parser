# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
