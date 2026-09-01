"""Image format of the lossless bitmap tags."""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag


class ImageBitmapType(Enum):
    """Image format of a `DefineBitsLosslessTag`."""

    OPAQUE_8BIT = auto()
    """
    8-bit image with a color table.

    Used when `DefineBitsLosslessTag.bitmap_format` is `FORMAT_8_BIT` and
    `DefineBitsLosslessTag.version` is 1.

    The property `DefineBitsLosslessTag.color_table` must be set.
    """

    OPAQUE_15BIT = auto()
    """
    15-bit image (5 bits for red, 5 bits for green, 5 bits for blue).

    Used when `DefineBitsLosslessTag.bitmap_format` is `FORMAT_15_BIT` and
    `DefineBitsLosslessTag.version` is 1.

    The property `DefineBitsLosslessTag.color_table` is not set.
    """

    OPAQUE_24BIT = auto()
    """
    True color image without alpha channel.

    Used when `DefineBitsLosslessTag.bitmap_format` is `FORMAT_24_BIT` and
    `DefineBitsLosslessTag.version` is 1.

    The property `DefineBitsLosslessTag.color_table` is not set.
    """

    TRANSPARENT_8BIT = auto()
    """
    8-bit image with a color table supporting transparency.

    Used when `DefineBitsLosslessTag.bitmap_format` is `FORMAT_8_BIT` and
    `DefineBitsLosslessTag.version` is 2.

    The property `DefineBitsLosslessTag.color_table` must be set.
    """

    TRANSPARENT_32BIT = auto()
    """
    32-bit image with alpha channel.

    Used when `DefineBitsLosslessTag.bitmap_format` is `FORMAT_32_BIT` and
    `DefineBitsLosslessTag.version` is 2.

    The property `DefineBitsLosslessTag.color_table` is not set.
    """

    @property
    def is_true_color(self) -> bool:
        return self in _TRUE_COLOR

    @classmethod
    def from_tag(cls, tag: DefineBitsLosslessTag) -> ImageBitmapType:
        """Resolve the format from a `DefineBitsLosslessTag`."""
        # The FORMAT_* constants are read from the tag instance to avoid importing the tag module.
        match tag.version:
            case 1:
                match tag.bitmap_format:
                    case tag.FORMAT_8_BIT:
                        return cls.OPAQUE_8BIT
                    case tag.FORMAT_15_BIT:
                        return cls.OPAQUE_15BIT
                    case tag.FORMAT_24_BIT:
                        return cls.OPAQUE_24BIT
                    case _:
                        raise ValueError(f"Unknown bitmap format for version 1: {tag.bitmap_format}")
            case 2:
                match tag.bitmap_format:
                    case tag.FORMAT_8_BIT:
                        return cls.TRANSPARENT_8BIT
                    case tag.FORMAT_32_BIT:
                        return cls.TRANSPARENT_32BIT
                    case _:
                        raise ValueError(f"Unknown bitmap format for version 2: {tag.bitmap_format}")
            case _:
                raise ValueError(f"Unknown version: {tag.version}")


_TRUE_COLOR = frozenset({ImageBitmapType.OPAQUE_24BIT, ImageBitmapType.TRANSPARENT_32BIT})
