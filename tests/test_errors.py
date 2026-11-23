"""Tests for cdindex_parser.errors — exception hierarchy."""

import pytest

from cdindex_parser.errors import (
    CDIndexError,
    EncodingError,
    IndentMismatchError,
    InputNotFoundError,
    LineCountMismatchError,
    MalformedRecordError,
)


class TestExceptionHierarchy:
    """Tests for the exception class hierarchy."""

    def test_cdindex_error_is_exception(self):
        assert issubclass(CDIndexError, Exception)

    def test_input_not_found_is_file_not_found(self):
        assert issubclass(InputNotFoundError, FileNotFoundError)
        assert issubclass(InputNotFoundError, CDIndexError)

    def test_encoding_error_is_unicode_decode_error(self):
        assert issubclass(EncodingError, UnicodeDecodeError)
        assert issubclass(EncodingError, CDIndexError)

    def test_line_count_mismatch_is_value_error(self):
        assert issubclass(LineCountMismatchError, ValueError)
        assert issubclass(LineCountMismatchError, CDIndexError)

    def test_indent_mismatch_is_value_error(self):
        assert issubclass(IndentMismatchError, ValueError)
        assert issubclass(IndentMismatchError, CDIndexError)

    def test_malformed_record_is_value_error(self):
        assert issubclass(MalformedRecordError, ValueError)
        assert issubclass(MalformedRecordError, CDIndexError)

    def test_catch_as_cdindex_error(self):
        """All specific errors should be catchable as CDIndexError."""
        for exc_class, args in [
            (InputNotFoundError, ("test",)),
            (LineCountMismatchError, ("test",)),
            (IndentMismatchError, ("test",)),
            (MalformedRecordError, ("test", 1)),
        ]:
            try:
                raise exc_class(*args)
            except CDIndexError:
                pass  # Expected
            else:
                pytest.fail(f"{exc_class.__name__} not catchable as CDIndexError")

    def test_encoding_error_is_catchable(self):
        """EncodingError extends UnicodeDecodeError which needs 5 args in __init__."""
        try:
            raise EncodingError("utf-8", b"", 0, 1, "test")
        except CDIndexError:
            pass  # Expected
        else:
            pytest.fail("EncodingError not catchable as CDIndexError")

    def test_malformed_record_has_line_number(self):
        exc = MalformedRecordError("bad line", line_number=42)
        assert exc.line_number == 42

    def test_malformed_record_line_number_optional(self):
        exc = MalformedRecordError("bad line")
        assert exc.line_number is None

    def test_errors_are_value_error_catchable(self):
        """ValueError-based errors should be catchable as ValueError."""
        for exc_class in [
            LineCountMismatchError,
            IndentMismatchError,
            MalformedRecordError,
        ]:
            try:
                raise exc_class("test")
            except ValueError:
                pass  # Expected
            else:
                pytest.fail(f"{exc_class.__name__} not catchable as ValueError")
