"""Fallback tag for any tag type the parser does not handle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.errors import Errors, UnknownTagError

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class UnknownTag:
    """
    Unknown tag.

    Can be used to represent a tag that is not yet implemented, an error, a custom tag, or an
    obfuscation mechanism.
    """

    code: int
    data: bytes

    @classmethod
    def create(cls, reader: Reader, code: int, end: int) -> Self:
        if reader.errors & Errors.UNKNOWN_TAG:
            raise UnknownTagError(code, reader.offset)

        return cls(code=code, data=reader.read_bytes_to(end))
