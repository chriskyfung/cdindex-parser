# API Reference

The public API of `cdindex-parser` is documented below. All types are frozen dataclasses and all functions are pure where possible.

## Core API

::: cdindex_parser.parse_catalog

::: cdindex_parser.Catalog

::: cdindex_parser.Entry

::: cdindex_parser.FileRecord

::: cdindex_parser.NameRecord

## Utilities

::: cdindex_parser.resolve_input_path

::: cdindex_parser.parser.decode_dos_datetime

::: cdindex_parser.to_csv

::: cdindex_parser.to_json

## Exceptions

All errors inherit from `CDIndexError`:

::: cdindex_parser.errors.CDIndexError

::: cdindex_parser.errors.InputNotFoundError

::: cdindex_parser.errors.EncodingError

::: cdindex_parser.errors.LineCountMismatchError

::: cdindex_parser.errors.IndentMismatchError

::: cdindex_parser.errors.MalformedRecordError
