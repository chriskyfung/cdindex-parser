"""Command-line interface for cdindex-parser."""

import argparse
import sys
from collections.abc import Sequence
from importlib import metadata
from pathlib import Path

from .exporters import to_csv, to_json
from .models import Catalog
from .parser import parse_catalog, resolve_input_path


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cdindex-parser",
        description="Parse CD Index 2 (光碟索引大師) IDX/FILE catalogs into CSV/JSON",
    )
    parser.add_argument(
        "input",
        help=(
            "Base name or path of the IDX/FILE pair "
            "(e.g. mydisk, mydisk.IDX, path/to/disk)"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Output file path (CSV or JSON, inferred from suffix unless overridden)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default=None,
        help="Output format (csv or json); default inferred from --output suffix",
    )
    parser.add_argument(
        "--encoding",
        default="utf-16",
        help="Input encoding (utf-16, big5, cp950); default utf-16 with BOM detection",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"cdindex-parser {metadata.version('cdindex-parser')}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and run the conversion pipeline.

    Returns an exit code suitable for ``sys.exit``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    idx_path, _ = resolve_input_path(args.input)
    try:
        catalog: Catalog = parse_catalog(args.input, encoding=args.encoding)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Determine output path and format
    output_path: str | Path
    fmt: str

    if args.output:
        output_path = Path(args.output)
        fmt = args.format or output_path.suffix.lstrip(".").lower() or "csv"
    else:
        # Default: same base name with .csv extension
        base = Path(idx_path).with_suffix("")
        output_path = base.with_suffix(".csv")
        fmt = "csv"

    if fmt == "csv":
        to_csv(catalog, output_path)
    elif fmt == "json":
        to_json(catalog, output_path)
    else:
        print(f"Error: unknown format '{fmt}'", file=sys.stderr)
        return 1

    print(f"Wrote {fmt.upper()} output to {output_path}")
    return 0
