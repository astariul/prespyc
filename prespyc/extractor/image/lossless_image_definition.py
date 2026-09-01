"""Image character extracted from a DefineBitsLossless tag."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from prespyc._util import php_mod
from prespyc.extractor.image.image_data import ImageData
from prespyc.extractor.image.pixels import ALPHA_TRANSPARENT, Pixels
from prespyc.parser.structure.record.image_bitmap_type import ImageBitmapType
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag


class LosslessImageDefinition:
    """
    A raw image extracted from a `DefineBitsLosslessTag`.

    A version 1 tag has no alpha channel, a version 2 tag has one. The best export format is PNG.
    """

    __slots__ = ("_bounds", "_pixels", "_png_data", "character_id", "tag")

    def __init__(self, tag: DefineBitsLosslessTag) -> None:
        self.tag = tag
        self.character_id = tag.character_id
        self._bounds: Rectangle | None = None
        self._pixels: Pixels | None = None
        self._png_data: bytes | None = None

    @property
    def bounds(self) -> Rectangle:
        if self._bounds is None:
            self._bounds = Rectangle(0, self.tag.bitmap_width * 20, 0, self.tag.bitmap_height * 20)

        return self._bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        from prespyc.extractor.image.transformed_image import TransformedImage

        return TransformedImage.from_png(self.character_id, self.bounds, color_transform, self.to_png())

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ImageCharacter:
        return modifier.apply_on_image(self)

    def to_base64_data(self) -> str:
        return "data:image/png;base64," + base64.b64encode(self.to_png()).decode("ascii")

    def to_png(self) -> bytes:
        if self._png_data is None:
            self._png_data = self._to_pixels().to_png()

        return self._png_data

    def to_jpeg(self, quality: int = -1) -> bytes:
        return self._to_pixels().to_jpeg(quality)

    def to_best_format(self) -> ImageData:
        return ImageData(ImageDataType.PNG, self.to_png())

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.image(self)

        return drawer

    def _to_pixels(self) -> Pixels:
        if self._pixels is not None:
            return self._pixels

        width = self.tag.bitmap_width
        height = self.tag.bitmap_height

        if width < 1 or height < 1:
            raise RuntimeError("Empty image is not supported")

        bitmap_type = self.tag.type
        pixels = Pixels.create(width, height) if bitmap_type.is_true_color else Pixels.with_palette(width, height)

        match bitmap_type:
            case ImageBitmapType.OPAQUE_8BIT:
                self._decode_8bit(pixels, width, height)
            case ImageBitmapType.OPAQUE_24BIT:
                self._decode_24bit(pixels)
            case ImageBitmapType.OPAQUE_15BIT:
                # @todo Opaque15Bit, there is no sample to test it against
                raise NotImplementedError("Opaque15Bit is not implemented yet")
            case ImageBitmapType.TRANSPARENT_8BIT:
                self._decode_8bit_with_alpha(pixels, width, height)
            case ImageBitmapType.TRANSPARENT_32BIT:
                self._decode_32bit_with_alpha(pixels)

        self._pixels = pixels

        return pixels

    def _decode_8bit(self, pixels: Pixels, width: int, height: int) -> None:
        color_table = self.tag.color_table

        if color_table is None:
            raise RuntimeError("Color table is missing for 8-bit image")

        for i in range(0, len(color_table), 3):
            pixels.allocate_color(color_table[i], color_table[i + 1], color_table[i + 2])

        self._set_color_map_pixels(pixels, width, height)

    def _decode_8bit_with_alpha(self, pixels: Pixels, width: int, height: int) -> None:
        color_table = self.tag.color_table

        if color_table is None:
            raise RuntimeError("Color table is missing for 8-bit image")

        for i in range(0, len(color_table), 4):
            pixels.allocate_color_alpha(
                color_table[i],
                color_table[i + 1],
                color_table[i + 2],
                ALPHA_TRANSPARENT - (color_table[i + 3] >> 1),  # GD alpha is 0 - 127
            )

        self._set_color_map_pixels(pixels, width, height)

    def _set_color_map_pixels(self, pixels: Pixels, width: int, height: int) -> None:
        # Each line is 32-bit aligned, so compute the padding size added at the end of the line
        padding_size = (4 - php_mod(width, 4)) & 3
        stride = width + padding_size
        data = self.tag.pixel_data
        indices = bytearray(width * height)

        for y in range(height):
            offset = y * stride
            # Padded so that truncated pixel data cannot resize the buffer: a short row falls back
            # on the first color of the table, where the original would raise on the missing byte.
            indices[y * width : (y + 1) * width] = data[offset : offset + width].ljust(width, b"\x00")

        pixels.write_indices(indices)

    def _decode_32bit_with_alpha(self, pixels: Pixels) -> None:
        # Colors are premultiplied by alpha, and a pixel with an alpha of 0 has no recoverable
        # color, so it becomes fully transparent.
        pixels.write_premultiplied_argb(self.tag.pixel_data)

    def _decode_24bit(self, pixels: Pixels) -> None:
        # The first byte of every pixel is ignored: pixels are 32-bit aligned.
        pixels.write_xrgb(self.tag.pixel_data)
