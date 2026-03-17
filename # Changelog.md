# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial parser for CD Index 2 `.IDX` and `.FILE` files
- Line-by-line structure matching algorithm
- CSV/JSON export with full path reconstruction
- Big5 encoding support for Traditional Chinese
- Stack-based directory tree reconstruction

### Changed

- N/A

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
