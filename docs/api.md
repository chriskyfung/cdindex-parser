# API Reference

The public API of `cdindex2-parser` is documented below. All types are frozen dataclasses and all functions are pure where possible.

## Core API

::: cdindex2_parser.parse_catalog

::: cdindex2_parser.Catalog

::: cdindex2_parser.Entry

::: cdindex2_parser.FileRecord

::: cdindex2_parser.NameRecord

## Utilities

::: cdindex2_parser.resolve_input_path

::: cdindex2_parser.parser.decode_dos_datetime

::: cdindex2_parser.to_csv

::: cdindex2_parser.to_json

## Exceptions

All errors inherit from `CDIndexError`:

::: cdindex2_parser.errors.CDIndexError

::: cdindex2_parser.errors.InputNotFoundError

::: cdindex2_parser.errors.EncodingError

::: cdindex2_parser.errors.LineCountMismatchError

::: cdindex2_parser.errors.IndentMismatchError

::: cdindex2_parser.errors.MalformedRecordError
