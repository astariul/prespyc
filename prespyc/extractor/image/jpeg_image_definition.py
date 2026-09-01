"""Image character extracted from a DefineBitsJPEG tag."""

from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from prespyc.extractor.image.image_data import ImageData
from prespyc.extractor.image.pixels import Pixels, fix_jpeg_data, image_size
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.image.transformed_image import TransformedImage
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.tag.define_bits_jpeg import DefineBitsJPEGTag


class JpegImageDefinition:
    """
    A raw image extracted from a `DefineBitsJPEG2`, `DefineBitsJPEG3` or `DefineBitsJPEG4` tag.

    Despite the tag names the payload may be a JPEG, a PNG or a GIF89a, and a JPEG payload may come
    with an alpha channel, so the exported image is usually a PNG.
    """

    __slots__ = ("_bounds", "_color_transform_cache", "_pixels", "_png_data", "character_id", "tag")

    def __init__(self, tag: DefineBitsJPEGTag) -> None:
        self.tag = tag
        self.character_id = tag.character_id
        self._bounds: Rectangle | None = None
        self._pixels: Pixels | None = None
        self._png_data: bytes | None = None

        # Last transformed images, keyed on the image so that they are dropped with it.
        self._color_transform_cache: weakref.WeakKeyDictionary[TransformedImage, ColorTransform] | None = None

    @property
    def bounds(self) -> Rectangle:
        if self._bounds is not None:
            return self._bounds

        data = self.tag.image_data

        if self.tag.type is ImageDataType.JPEG:
            data = fix_jpeg_data(data)

        size = image_size(data)

        if size is None:
            raise RuntimeError("Invalid JPEG data")

        width, height = size
        self._bounds = Rectangle(0, width * 20, 0, height * 20)

        return self._bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        from prespyc.extractor.image.transformed_image import TransformedImage

        cache = self._color_transform_cache

        if cache is None:
            cache = self._color_transform_cache = weakref.WeakKeyDictionary()

        for image, other_transform in cache.items():
            if other_transform == color_transform:
                return image

        if self.tag.type is ImageDataType.JPEG and self.tag.alpha_data is None:
            transformed = TransformedImage.from_jpeg(
                self.character_id, self.bounds, color_transform, self.tag.image_data
            )
        else:
            transformed = TransformedImage.from_png(self.character_id, self.bounds, color_transform, self.to_png())

        cache[transformed] = color_transform

        return transformed

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ImageCharacter:
        return modifier.apply_on_image(self)

    def to_base64_data(self) -> str:
        return self.to_best_format().base64_url

    def to_png(self) -> bytes:
        if self.tag.type is ImageDataType.PNG:
            return self.tag.image_data

        if self._png_data is None:
            self._png_data = self._to_pixels().to_png()

        return self._png_data

    def to_jpeg(self, quality: int = -1) -> bytes:
        if self.tag.type is ImageDataType.JPEG and self.tag.alpha_data is None:
            return fix_jpeg_data(self.tag.image_data)

        return self._to_pixels().to_jpeg(quality)

    def to_best_format(self) -> ImageData:
        if self.tag.type is ImageDataType.JPEG and self.tag.alpha_data is None:
            return ImageData(ImageDataType.JPEG, fix_jpeg_data(self.tag.image_data))

        return ImageData(ImageDataType.PNG, self.to_png())

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.image(self)

        return drawer

    def _to_pixels(self) -> Pixels:
        # @todo handle deblock_param on the v4 tag
        if self._pixels is None:
            match self.tag.type:
                case ImageDataType.PNG:
                    self._pixels = Pixels.from_png(self.tag.image_data)
                case ImageDataType.GIF89A:
                    self._pixels = self._parse_gif_data()
                case ImageDataType.JPEG:
                    self._pixels = self._parse_jpeg_data()

        return self._pixels

    def _parse_gif_data(self) -> Pixels:
        raise NotImplementedError("Not implemented")

    def _parse_jpeg_data(self) -> Pixels:
        pixels = Pixels.from_jpeg(self.tag.image_data)
        alpha_data = self.tag.alpha_data

        if alpha_data:
            pixels.apply_alpha_plane(alpha_data)

        return pixels
