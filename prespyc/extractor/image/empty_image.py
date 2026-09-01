"""Fallback image character, for an invalid or missing image."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from prespyc.extractor.image.image_data import ImageData
from prespyc.extractor.image.pixels import Pixels
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform

_BOUNDS = Rectangle(0, 20, 0, 20)
"""20x20 twips, so 1x1 pixel."""


@dataclass(frozen=True, slots=True)
class EmptyImage:
    """Fallback type for an invalid or missing image: a single opaque black pixel."""

    PNG_DATA: ClassVar[bytes] = (
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x00\x37\x6e\xf9"
        b"\x24\x00\x00\x00\x0a\x49\x44\x41\x54\x78\x01\x63\x60\x00\x00\x00"
        b"\x02\x00\x01\x73\x75\x01\x18\x00\x00\x00\x00\x49\x45\x4e\x44\xae"
        b"\x42\x60\x82"
    )

    character_id: int

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.image(self)

        return drawer

    @property
    def bounds(self) -> Rectangle:
        return _BOUNDS

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        from prespyc.extractor.image.transformed_image import TransformedImage

        return TransformedImage.from_png(self.character_id, self.bounds, color_transform, self.PNG_DATA)

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ImageCharacter:
        return modifier.apply_on_image(self)

    def to_base64_data(self) -> str:
        return self.to_best_format().base64_url

    def to_png(self) -> bytes:
        return self.PNG_DATA

    def to_jpeg(self, quality: int = -1) -> bytes:
        # Note: the original ignores the requested quality here.
        return Pixels.from_png(self.PNG_DATA).to_jpeg()

    def to_best_format(self) -> ImageData:
        return ImageData(ImageDataType.PNG, self.PNG_DATA)
