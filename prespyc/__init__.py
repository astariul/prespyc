"""
prespyc — SWF parsing and resource extraction in pure Python.

The public surface is assembled in Phase 7 of the port; see `PLAN.md`.
"""

from __future__ import annotations

from prespyc.errors import (
    CircularReferenceError,
    Errors,
    ExtractorError,
    ExtraDataError,
    InvalidDataError,
    OutOfBoundsError,
    ParserError,
    ProcessingInvalidDataError,
    SwfError,
    UnknownTagError,
)

__all__ = [
    "CircularReferenceError",
    "Errors",
    "ExtraDataError",
    "ExtractorError",
    "InvalidDataError",
    "OutOfBoundsError",
    "ParserError",
    "ProcessingInvalidDataError",
    "SwfError",
    "UnknownTagError",
]
