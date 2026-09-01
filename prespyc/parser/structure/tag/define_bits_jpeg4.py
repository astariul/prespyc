"""DefineBitsJPEG4 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.image_data_type import ImageDataType

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineBitsJPEG4Tag:
    """
    Like `DefineBitsJPEG3Tag`, with a deblocking filter parameter. Implements `DefineBitsJPEGTag`.

    Despite the tag name, the payload can be a JPEG, a PNG or a GIF89a image.
    """

    TYPE: ClassVar[int] = 90

    character_id: int
    deblock_param: int

    image_data: bytes
    """Raw image data. Can be JPEG, PNG or GIF89a."""

    alpha_data: bytes | None
    """
    Uncompressed alpha data as a byte array.

    Each byte is the opacity of the corresponding pixel in `image_data`. The length of this array
    must be equal to the decoded image width * height.

    Note: this field is only present if `image_data` is a JPEG image.
    """

    @property
    def type(self) -> ImageDataType:
        """The stored image data type."""
        return ImageDataType.resolve(self.image_data)

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a DefineBitsJPEG4 tag, whose data ends at the `end` byte offset."""
        character_id = reader.read_ui16()
        alpha_data_offset = reader.read_ui32()
        deblock_param = reader.read_ui16()
        image_data = reader.read_bytes(alpha_data_offset)
        alpha_data = None

        if end > reader.offset:
            alpha_data = reader.read_zlib_to(end)

            if alpha_data == b"":
                alpha_data = None

        return cls(
            character_id=character_id,
            deblock_param=deblock_param,
            image_data=image_data,
            alpha_data=alpha_data,
        )
