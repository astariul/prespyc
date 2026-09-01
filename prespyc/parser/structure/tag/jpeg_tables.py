"""JPEGTables tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class JPEGTablesTag:
    """The JPEG encoding tables shared by every `DefineBitsTag` that follows it."""

    TYPE: ClassVar[int] = 8

    data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a JPEGTables tag, whose data ends at the `end` byte offset."""
        return cls(reader.read_bytes_to(end))
