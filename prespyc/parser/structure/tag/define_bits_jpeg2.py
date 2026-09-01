"""DefineBitsJPEG2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.image_data_type import ImageDataType

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineBitsJPEG2Tag:
    """
    A self-contained image character. Implements `DefineBitsJPEGTag`.

    Despite the tag name, the payload can be a JPEG, a PNG or a GIF89a image.
    """

    TYPE: ClassVar[int] = 21

    character_id: int
    image_data: bytes

    @property
    def type(self) -> ImageDataType:
        """The stored image data type."""
        return ImageDataType.resolve(self.image_data)

    @property
    def alpha_data(self) -> bytes | None:
        """Always `None`: this tag carries no separate alpha channel."""
        return None

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineBitsJPEG2 tag, whose data ends at the `end` byte offset."""
        return cls(
            character_id=reader.read_ui16(),
            image_data=reader.read_bytes_to(end),
        )
