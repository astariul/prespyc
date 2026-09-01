"""DefineBitsLossless and DefineBitsLossless2 tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.structure.record.image_bitmap_type import ImageBitmapType

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineBitsLosslessTag:
    """A ZLib-compressed bitmap character, without (v1) or with (v2) an alpha channel."""

    TYPE_V1: ClassVar[int] = 20
    TYPE_V2: ClassVar[int] = 36

    FORMAT_8_BIT: ClassVar[int] = 3
    FORMAT_15_BIT: ClassVar[int] = 4
    """Only on v1"""
    FORMAT_24_BIT: ClassVar[int] = 5
    """Only on v1"""
    FORMAT_32_BIT: ClassVar[int] = 5
    """Only on v2 — same tag code as `FORMAT_24_BIT`, the version tells them apart."""

    version: int
    character_id: int
    bitmap_format: int

    bitmap_width: int
    """Swf spec allow 0 width and height, but this is not a valid image"""

    bitmap_height: int
    """Swf spec allow 0 width and height, but this is not a valid image"""

    color_table: bytes | None

    pixel_data: bytes
    """
    Uncompressed pixel data.

    The content depends on `bitmap_format`:
    - `FORMAT_8_BIT`: 1 byte per pixel, use the `color_table` to get the color
    - `FORMAT_15_BIT`: 2 bytes per pixel, 5 bits for red, 5 bits for green, 5 bits for blue
      (first bit is ignored)
    - `FORMAT_24_BIT`: 3 bytes per pixel, 8 bits for red, 8 bits for green, 8 bits for blue
      (first byte is ignored)
    - `FORMAT_32_BIT`: 4 bytes per pixel, 8 bits for alpha, 8 bits for red, 8 bits for green,
      8 bits for blue
    """

    @property
    def type(self) -> ImageBitmapType:
        """Get the sorted image format"""
        return ImageBitmapType.from_tag(self)

    @classmethod
    def read(cls, reader: Reader, version: int, end: int) -> Self:
        """
        Read a DefineBitsLossless or DefineBitsLossless2 tag from the reader.

        `version` is 1 for DefineBitsLossless and 2 for DefineBitsLossless2. `end` is the end
        position of the tag in the stream, used to determine the end of the pixel data.
        """
        character_id = reader.read_ui16()
        bitmap_format = reader.read_ui8()
        bitmap_width = reader.read_ui16()
        bitmap_height = reader.read_ui16()

        if (bitmap_format < 3 or bitmap_format > 5) and reader.errors & Errors.INVALID_DATA:
            raise InvalidDataError(
                f"Invalid bitmap format {bitmap_format} for DefineBitsLossless tag (version {version})",
                reader.offset,
            )

        if bitmap_format == cls.FORMAT_8_BIT:
            colors = reader.read_ui8()
            data = reader.read_zlib_to(end)
            color_size = 4 if version > 1 else 3  # 4 bytes for RGBA, 3 bytes for RGB
            color_table_size = color_size * (colors + 1)

            color_table = data[0:color_table_size]
            pixel_data = data[color_table_size:]
        else:
            color_table = None
            pixel_data = reader.read_zlib_to(end)

        return cls(
            version=version,
            character_id=character_id,
            bitmap_format=bitmap_format,
            bitmap_width=bitmap_width,
            bitmap_height=bitmap_height,
            color_table=color_table,
            pixel_data=pixel_data,
        )
