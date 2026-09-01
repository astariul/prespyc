"""Error flags and exception types."""

from __future__ import annotations

from enum import IntFlag


class Errors(IntFlag):
    """
    Flags selecting which malformed-data conditions raise instead of falling back.

    If the bit for an error is set, an exception is raised when that error occurs. If not, the
    error is silently ignored and a fallback value is used instead.

    Enabling everything stops parsing on the first malformed or unexpected byte, which is safer but
    fails on some legitimate (sloppily authored) SWF files. Disabling everything gives fail-safe
    parsing that extracts as much as possible from corrupted files, at the cost of unexpected
    results.
    """

    NONE = 0
    """Disable all error flags."""

    OUT_OF_BOUNDS = 1
    """Trying to access data after the end of the input stream."""

    INVALID_DATA = 2
    """The input data is invalid or corrupted."""

    EXTRA_DATA = 4
    """The input data has more data than expected (i.e. not all data was consumed)."""

    UNKNOWN_TAG = 8
    """The tag code is unknown or not supported."""

    INVALID_TAG = 16
    """
    An error occurred while reading a tag.

    If this flag is not set, the tag is skipped when an error occurs, so all other errors are
    ignored for that tag. Enabling everything except this flag gives a good balance between
    detecting invalid tags and fail-safe reading.

    No exception is associated with this flag: it only selects whether an invalid tag is skipped or
    the parsing error is raised.
    """

    CIRCULAR_REFERENCE = 32
    """A circular reference was detected while processing a display list or timeline."""

    UNPROCESSABLE_DATA = 64
    """
    The data was parsed successfully (i.e. the format is valid) but cannot be processed, due to
    missing or incoherent data.
    """

    ALL = (
        OUT_OF_BOUNDS | INVALID_DATA | EXTRA_DATA | UNKNOWN_TAG | INVALID_TAG | CIRCULAR_REFERENCE | UNPROCESSABLE_DATA
    )
    """Enable all error flags."""

    IGNORE_INVALID_TAG = ALL & ~INVALID_TAG
    """Enable all errors, but skip invalid tags instead of raising."""


class SwfError(Exception):
    """Base type for all prespyc exceptions."""


class ParserError(SwfError):
    """Base type for all parser exceptions."""

    def __init__(self, message: str, offset: int) -> None:
        super().__init__(message)
        self.offset = offset
        """The offset in the input stream where the error occurred."""


class OutOfBoundsError(ParserError, IndexError):
    """The parser tried to access data after the end of the input stream."""

    @classmethod
    def read_after_end(cls, offset: int, end: int) -> OutOfBoundsError:
        return cls(f"Trying to access data after the end of the input stream (offset: {offset}, end: {end})", offset)

    @classmethod
    def read_too_many_bytes(cls, offset: int, end: int, num: int) -> OutOfBoundsError:
        return cls(f"Cannot read {num} bytes from offset {offset}, end is at {end}", offset)


class InvalidDataError(ParserError, ValueError):
    """The input data is invalid or corrupted."""

    @classmethod
    def invalid_compressed_data(cls, offset: int, reason: str = "Unknown error") -> InvalidDataError:
        return cls(f"Invalid compressed data at offset {offset}: {reason}", offset)


class ExtraDataError(ParserError, ValueError):
    """The input data holds more data than expected (i.e. not everything was consumed)."""

    def __init__(self, message: str, offset: int, length: int) -> None:
        super().__init__(message, offset)
        self.length = length
        """The amount of unconsumed data, in bytes."""


class UnknownTagError(ParserError, ValueError):
    """An unknown tag was found in the SWF file."""

    def __init__(self, tag_code: int, offset: int) -> None:
        super().__init__(f"Unknown tag with code {tag_code} at offset {offset}", offset)
        self.tag_code = tag_code


class ExtractorError(SwfError):
    """Base type for all extractor exceptions."""


class CircularReferenceError(ExtractorError):
    """A character references itself, directly or through its display list."""

    def __init__(self, message: str, character_id: int) -> None:
        super().__init__(message)
        self.character_id = character_id
        """Character id the cycle was detected on."""


class ProcessingInvalidDataError(ExtractorError, ValueError):
    """
    The data was parsed successfully but cannot be processed, because it is missing or incoherent.
    """
