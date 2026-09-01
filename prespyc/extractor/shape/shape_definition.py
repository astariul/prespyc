"""A single shape character extracted from a SWF file."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.extractor.shape.shape import Shape
    from prespyc.extractor.shape.shape_processor import ShapeProcessor
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle
    from prespyc.parser.structure.tag.define_shape import DefineShapeTag
    from prespyc.parser.structure.tag.define_shape4 import DefineShape4Tag


class ShapeDefinition:
    """
    A shape character: the raw `DefineShapeTag` (or `DefineShape4Tag`) and the `Shape` it processes
    into.
    """

    __slots__ = ("_processor", "_shape", "id", "tag")

    def __init__(
        self,
        processor: ShapeProcessor,
        id: int,
        tag: DefineShapeTag | DefineShape4Tag,
    ) -> None:
        self._processor: ShapeProcessor | None = processor
        self._shape: Shape | None = None

        self.id = id
        """The character id of the shape."""

        self.tag = tag
        """The raw tag extracted from the SWF file."""

    @property
    def shape(self) -> Shape:
        """The shape object. Processed on the first call, then cached."""
        shape = self._shape

        if shape is None:
            processor = self._processor
            assert processor is not None

            self._shape = shape = processor.process(self.tag)
            self._processor = None  # Remove the processor to free memory

        return shape

    @property
    def bounds(self) -> Rectangle:
        return self.tag.shape_bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        drawer.shape(self.shape)

        return drawer

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> ShapeDefinition:
        return modifier.apply_on_shape(self)

    def to_svg(self, subpixel_stroke_width: bool = True) -> str:
        """
        The shape as an SVG string.

        Without `subpixel_stroke_width`, the minimum stroke width is 1px, which approximates Flash
        rendering.
        """
        from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas

        return self.draw(SvgCanvas(self.bounds, subpixel_stroke_width)).render()

    def transform_colors(self, color_transform: ColorTransform) -> ShapeDefinition:
        shape = self.shape.transform_colors(color_transform)

        new = copy.copy(self)
        new._shape = shape

        return new
