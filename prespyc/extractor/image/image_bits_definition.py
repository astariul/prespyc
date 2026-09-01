"""Image character extracted from a DefineBits tag."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from prespyc.extractor.image.image_data import ImageData
from prespyc.extractor.image.pixels import Pixels, fix_jpeg_data, image_size
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.tag.define_bits import DefineBitsTag
    from prespyc.parser.structure.tag.jpeg_tables import JPEGTablesTag


class ImageBitsDefinition:
    """
    A raw image extracted from a `DefineBitsTag`.

    Unlike `JpegImageDefinition` this only handles JPEG images, and needs the `JPEGTablesTag` that
    holds their encoding tables.
    """

    __slots__ = ("_bounds", "_fixed_jpeg_data", "character_id", "jpeg_tables", "tag")

    def __init__(self, tag: DefineBitsTag, jpeg_tables: JPEGTablesTag) -> None:
        self.tag = tag
        self.jpeg_tables = jpeg_tables
        self.character_id = tag.character_id
        self._bounds: Rectangle | None = None
        self._fixed_jpeg_data: bytes | None = None

    @property
    def bounds(self) -> Rectangle:
        if self._bounds is not None:
            return self._bounds

        size = image_size(self.to_jpeg())

        if size is None:
            raise RuntimeError("Invalid JPEG data")

        width, height = size
        self._bounds = Rectangle(0, width * 20, 0, height * 20)

        return self._bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        from prespyc.extractor.image.transformed_image import TransformedImage

        return TransformedImage.from_jpeg(self.character_id, self.bounds, color_transform, self.to_jpeg())

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ImageCharacter:
        return modifier.apply_on_image(self)

    def to_base64_data(self) -> str:
        return "data:image/jpeg;base64," + base64.b64encode(self.to_jpeg()).decode("ascii")

    def to_png(self) -> bytes:
        return Pixels.from_jpeg(self.jpeg_tables.data + self.tag.image_data).to_png()

    def to_jpeg(self, quality: int = -1) -> bytes:
        if self._fixed_jpeg_data is None:
            self._fixed_jpeg_data = fix_jpeg_data(self.jpeg_tables.data + self.tag.image_data)

        return self._fixed_jpeg_data

    def to_best_format(self) -> ImageData:
        return ImageData(ImageDataType.JPEG, self.to_jpeg())

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.image(self)

        return drawer
