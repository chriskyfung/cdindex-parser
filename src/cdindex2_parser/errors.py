"""Exception hierarchy for cdindex2-parser."""


class CDIndexError(Exception):
    """Base exception for all cdindex2-parser errors."""


class InputNotFoundError(CDIndexError, FileNotFoundError):
    """Raised when an input file cannot be found."""


class EncodingError(CDIndexError, UnicodeDecodeError):
    """Raised when the input encoding is incorrect."""


class LineCountMismatchError(CDIndexError, ValueError):
    """Raised when .IDX and .FILE line counts differ."""


class IndentMismatchError(CDIndexError, ValueError):
    """Raised when an indentation mismatch is found."""


class MalformedRecordError(CDIndexError, ValueError):
    """Raised when a record cannot be parsed."""

    def __init__(self, message: str, line_number: int | None = None):
        """Initialize with an optional line number for error context."""
        self.line_number = line_number
        super().__init__(message)
