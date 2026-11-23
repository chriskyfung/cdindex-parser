"""Core parsing logic for cdindex-parser IDX/FILE catalogs."""

from datetime import datetime
from pathlib import Path

from .errors import MalformedRecordError
from .models import Catalog, Entry, FileRecord, NameRecord


def resolve_input_path(input_path: str) -> tuple[str, str]:
    """Convert a base path or suffixed path into (.IDX path, .FILE path).

    The old code used ``input_path.rstrip('.IDX').rstrip('.FILE')`` which
    treats the argument as a *character set*, corrupting names like
    ``MyID.IDX`` → ``My`` and ``GAME.IDX`` → ``GAM``.

    This function correctly strips only the recognised suffixes and
    guarantees the returned pair has the same base name.
    """
    p = Path(input_path)
    stem = p.name
    if stem.endswith(".IDX"):
        stem = stem[:-4]  # strip .IDX  (4 chars)
    elif stem.endswith(".FILE"):
        stem = stem[:-5]  # strip .FILE (5 chars)
    # else: keep the original stem (base name only)
    base = p.parent / stem if p.parent else Path(stem)
    idx_path = str(base.with_suffix(".IDX"))
    file_path = str(base.with_suffix(".FILE"))
    return idx_path, file_path


def decode_dos_datetime(ts: int) -> datetime:
    """Decode a 32-bit DOS FAT timestamp into a ``datetime``.

    Parameters
    ----------
    ts : int
        32-bit integer timestamp in MS-DOS FAT ``dosdate`` format.

    Returns
    -------
    datetime
        ``datetime`` object; ``1970-01-01T00:00:00`` if the timestamp
        is negative or the date is invalid.

    """
    if ts < 0:
        return datetime(1970, 1, 1)

    dos_time = ts & 0xFFFF
    dos_date = ts >> 16

    sec = (dos_time & 0x1F) * 2
    minute = (dos_time >> 5) & 0x3F
    hour = dos_time >> 11

    day = dos_date & 0x1F
    month = (dos_date >> 5) & 0xF
    year = (dos_date >> 9) + 1980

    try:
        return datetime(year, month, day, hour, minute, sec)
    except ValueError:
        return datetime(1970, 1, 1)


def parse_file_line(line: str) -> FileRecord:
    """Parse a single line from a ``.FILE`` file.

    Parameters
    ----------
    line : str
        A single line from a ``.FILE`` file, expected format
        ``[D|F]<size>.<timestamp>``.

    Returns
    -------
    FileRecord
        A ``FileRecord`` dataclass instance.

    Raises
    ------
    MalformedRecordError
        If the line does not match the expected format.

    """
    stripped = line.lstrip("\t")
    s = stripped.rstrip("\n\r")

    if s.startswith(("D", "F")):
        t = s[0]
        try:
            size_part, ts_part = s[1:].split(".", 1)
        except ValueError as exc:
            raise MalformedRecordError(
                "malformed D/F line (expected '<D|F>.<size>.<ts>')"
            ) from exc

        size = int(size_part)
        ts = int(ts_part)

        return FileRecord(
            indent=len(line) - len(stripped),
            type=t,
            size=size,
            ts=ts,
            mtime=decode_dos_datetime(ts),
        )
    else:
        raise MalformedRecordError("not a D/F line")


def parse_name_line(line: str) -> NameRecord:
    """Parse a single line from a ``.IDX`` file.

    Parameters
    ----------
    line : str
        A single line from a ``.IDX`` file, expected to be tab-indented.

    Returns
    -------
    NameRecord
        A ``NameRecord`` dataclass instance.

    """
    from .models import NameRecord

    stripped = line.lstrip("\t")
    name = stripped.rstrip("\n\r")
    indent = len(line) - len(stripped)
    return NameRecord(indent=indent, name=name)


def parse_catalog(
    input_path: str | Path,
    *,
    encoding: str = "utf-16",
) -> Catalog:
    """Parse a ``.IDX``/``.FILE`` pair and return a ``Catalog``.

    Parameters
    ----------
    input_path : str | Path
        Base name or path of the IDX/FILE pair.  The suffix ``.IDX`` or
        ``.FILE`` is recognised; otherwise ``.IDX`` is appended.
    encoding : str, optional
        Text encoding for the input files.  Defaults to ``"utf-16"`` (BOM-
        detected).  Other common encodings such as ``"big5"`` or
        ``"cp950"`` may be selected if the original files use a different
        charset.

    Returns
    -------
    Catalog
        A ``Catalog`` containing the parsed entries.

    Raises
    ------
    InputNotFoundError
        If either the ``.IDX`` or ``.FILE`` file does not exist.
    LineCountMismatchError
        If the two files have a different number of non-empty lines.
    IndentMismatchError
        If a data line and its corresponding name line have different
        indentation.
    MalformedRecordError
        If any line cannot be parsed.

    """
    from .errors import IndentMismatchError, InputNotFoundError, LineCountMismatchError

    idx_path, file_path = resolve_input_path(str(input_path))

    try:
        with open(file_path, encoding=encoding, errors="replace") as f:
            file_lines = f.readlines()
    except FileNotFoundError as exc:
        raise InputNotFoundError(f"FILE not found: {file_path}") from exc

    try:
        with open(idx_path, encoding=encoding, errors="replace") as f:
            idx_lines = f.readlines()
    except FileNotFoundError as exc:
        raise InputNotFoundError(f"IDX not found: {idx_path}") from exc

    # Filter out empty lines
    file_lines = [line for line in file_lines if line.strip()]
    idx_lines = [line for line in idx_lines if line.strip()]

    if len(file_lines) != len(idx_lines):
        raise LineCountMismatchError(
            f"line count mismatch: {len(file_lines)} in .FILE, {len(idx_lines)} in .IDX"
        )

    entries: list[Entry] = []
    stack: list[str] = []  # path components
    for i, (f_line, n_line) in enumerate(zip(file_lines, idx_lines, strict=False)):
        try:
            fld = parse_file_line(f_line)
        except MalformedRecordError as exc:
            raise MalformedRecordError(
                f"error parsing .FILE line {i + 1}", line_number=i + 1
            ) from exc

        try:
            named = parse_name_line(n_line)
        except Exception as exc:
            raise MalformedRecordError(
                f"error parsing .IDX line {i + 1}", line_number=i + 1
            ) from exc

        if fld.indent != named.indent:
            raise IndentMismatchError(
                f"indent mismatch at line {i + 1}: "
                f".FILE has indent {fld.indent}, .IDX has indent {named.indent}"
            )

        # Build the entry path using a stack-based algorithm
        depth = named.indent
        while len(stack) > depth:
            stack.pop()
        stack.append(named.name)
        path = "/".join(stack)

        entries.append(
            Entry(
                depth=depth,
                name=named.name,
                is_dir=fld.type == "D",
                size_bytes=fld.size,
                mtime=fld.mtime,
                path=path,
            )
        )

    return Catalog(entries=tuple(entries))


def match_and_dump(
    input_path: str | Path,
    out_path: str | Path,
    encoding: str = "utf-16",
) -> None:
    """Compatibility wrapper that mimics the original ``match_and_dump``.

    .. deprecated:: 0.3.0
        Use ``cdindex_parser.parse_catalog`` + ``cdindex_parser.exporters``
        instead.
    """
    from .exporters import to_csv

    catalog = parse_catalog(input_path, encoding=encoding)
    to_csv(catalog, out_path)
