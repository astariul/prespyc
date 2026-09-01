"""DefineBits tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineBitsTag:
    """
    A JPEG image whose encoding tables are stored apart, in a `JPEGTablesTag`.

    `image_data` alone is not a decodable JPEG stream: it must be prefixed by the
    `JPEGTablesTag.data` of the preceding tables tag.
    """

    TYPE: ClassVar[int] = 6

    character_id: int
    image_data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineBits tag, whose data ends at the `end` byte offset."""
        return cls(
            character_id=reader.read_ui16(),
            image_data=reader.read_bytes_to(end),
        )
