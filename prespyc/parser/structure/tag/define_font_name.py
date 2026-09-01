"""DefineFontName tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineFontNameTag:
    """The full name and copyright of an embedded font."""

    TYPE: ClassVar[int] = 88

    font_id: int
    font_name: bytes
    font_copyright: bytes

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a DefineFontName tag from the reader."""
        return cls(
            font_id=reader.read_ui16(),
            font_name=reader.read_null_terminated_string(),
            font_copyright=reader.read_null_terminated_string(),
        )
