"""Image character with a color transform applied."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from prespyc.extractor.image.image_data import ImageData
from prespyc.extractor.image.pixels import Pixels
from prespyc.parser.structure.record.image_data_type import ImageDataType

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle


class TransformedImage:
    """
    An image character with a color transform applied, storing the transformed pixels directly.

    Build one with `from_png()`, `from_jpeg()` or `from_pixels()`, which say what the source data
    is; the transform itself is only applied when the PNG is asked for.
    """

    __slots__ = (
        "__weakref__",
        "_base_png_data",
        "_bounds",
        "_color_transform",
        "_transformed_png_data",
        "character_id",
    )

    def __init__(
        self,
        character_id: int,
        bounds: Rectangle,
        base_png_data: bytes,
        color_transform: ColorTransform,
    ) -> None:
        self.character_id = character_id
        self._bounds = bounds
        self._base_png_data = base_png_data
        self._color_transform = color_transform
        self._transformed_png_data: bytes | None = None

    @property
    def bounds(self) -> Rectangle:
        return self._bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        return TransformedImage(
            self.character_id,
            self._bounds,
            self._base_png_data,
            self._color_transform.append(color_transform),
        )

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ImageCharacter:
        return modifier.apply_on_image(self)

    def to_base64_data(self) -> str:
        return "data:image/png;base64," + base64.b64encode(self.to_png()).decode("ascii")

    def to_png(self) -> bytes:
        if self._transformed_png_data is not None:
            return self._transformed_png_data

        pixels = Pixels.from_png(self._base_png_data)
        pixels.transform_colors(self._color_transform)

        self._transformed_png_data = pixels.to_png()

        return self._transformed_png_data

    def to_jpeg(self, quality: int = -1) -> bytes:
        return Pixels.from_png(self.to_png()).to_jpeg(quality)

    def to_best_format(self) -> ImageData:
        return ImageData(ImageDataType.PNG, self.to_png())

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.image(self)

        return drawer

    @classmethod
    def from_png(
        cls,
        character_id: int,
        bounds: Rectangle,
        color_transform: ColorTransform,
        png_data: bytes,
    ) -> TransformedImage:
        """Apply the color transform to PNG data. `character_id` and `bounds` are the original's."""
        return cls(character_id, bounds, png_data, color_transform)

    @classmethod
    def from_jpeg(
        cls,
        character_id: int,
        bounds: Rectangle,
        color_transform: ColorTransform,
        jpeg_data: bytes,
    ) -> TransformedImage:
        """Apply the color transform to JPEG data. `character_id` and `bounds` are the original's."""
        return cls.from_pixels(character_id, bounds, color_transform, Pixels.from_jpeg(jpeg_data))

    @classmethod
    def from_pixels(
        cls,
        character_id: int,
        bounds: Rectangle,
        color_transform: ColorTransform,
        image: Pixels,
    ) -> TransformedImage:
        """Apply the color transform to a decoded buffer. `character_id` and `bounds` are the original's."""
        return cls(character_id, bounds, image.to_png(), color_transform)
