"""DefineBinaryData tag: an opaque blob attached to a character id."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineBinaryDataTag:
    """Arbitrary binary data, embedded by the authoring tool for an AS3 class."""

    TYPE: ClassVar[int] = 87

    tag: int
    data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        tag = reader.read_ui16()
        reader.skip_bytes(4)  # Reserved, must be 0

        data = reader.read_bytes_to(end)

        return cls(tag, data)
