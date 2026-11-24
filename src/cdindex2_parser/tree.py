"""Path reconstruction for cdindex2-parser catalog trees."""

from collections.abc import Iterator


def build_paths(entries: Iterator[tuple[int, str]]) -> Iterator[str]:
    r"""Reconstruct full paths from a (depth, name) iterator using tab indentation.

    Walks the entry tree maintaining a stack of path components.
    Each entry's depth (number of leading tabs) determines when items
    are popped from the stack.

    Parameters
    ----------
    entries : Iterator[tuple[int, str]]
        Sequence of (depth, name) pairs, typically from ``parse_name_line``
        or generated from a ``Catalog``\ 's entries.

    Yields
    ------
    str
        Full path composed of forward-slashes, e.g. ``"dir/sub/file"``.

    """
    stack: list[str] = []
    for depth, name in entries:
        while len(stack) > depth:
            stack.pop()
        stack.append(name)
        yield "/".join(stack)
