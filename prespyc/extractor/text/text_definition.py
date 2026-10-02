"""A SWF static text character, and the fonts it is drawn with."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.extractor.shape.shape_builder import ShapeBuilder
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.extractor import Extractor
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.extractor.shape.shape_definition import ShapeDefinition
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle
    from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
    from prespyc.parser.structure.tag.define_text import DefineTextTag


@dataclass(frozen=True, slots=True)
class Font:
    """The glyph shapes of a font."""

    id: int

    em_square: int
    """Size of the EM square the glyphs are drawn in: 1024, or 20480 from DefineFont3 on."""

    glyphs: list[list[ShapeRecord]]

    def glyph(self, index: int, color: Color, extractor: Extractor) -> ShapeDefinition:
        """The glyph at `index`, filled with `color`, as a shape in EM square units."""
        builder = ShapeBuilder(extractor).fill(FillStyle(FillStyle.SOLID, color=color))
        x = y = 0

        for record in self.glyphs[index]:
            if isinstance(record, StyleChangeRecord):
                if record.state_move_to:
                    x, y = record.move_delta_x, record.move_delta_y
                    builder.move_to(x, y)
            elif isinstance(record, StraightEdgeRecord):
                x, y = x + record.delta_x, y + record.delta_y
                builder.line_to(x, y)
            elif isinstance(record, CurvedEdgeRecord):
                control_x, control_y = x + record.control_delta_x, y + record.control_delta_y
                x, y = control_x + record.anchor_delta_x, control_y + record.anchor_delta_y
                builder.curve_to(control_x, control_y, x, y)

        return builder.build(self.id)


class TextDefinition:
    """
    A static text character: runs of glyphs, each drawn with the glyph shape of its font.

    It draws as a one-frame timeline of glyphs, sized by the bounds the tag declares.
    """

    __slots__ = ("_extractor", "_timeline", "id", "tag")

    def __init__(self, extractor: Extractor, id: int, tag: DefineTextTag) -> None:
        self._extractor: Extractor | None = extractor
        self._timeline: Timeline | None = None

        self.id = id
        """Character id of the text."""

        self.tag = tag
        """The raw SWF tag."""

    @property
    def timeline(self) -> Timeline:
        """The glyphs, placed on first access and cached afterwards."""
        if self._timeline is None:
            self._timeline = self._place_glyphs()
            self._extractor = None  # Remove the extractor to remove cyclic reference

        return self._timeline

    @property
    def bounds(self) -> Rectangle:
        return self.tag.text_bounds

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        return self.timeline.draw(drawer, frame)

    def transform_colors(self, color_transform: ColorTransform) -> TextDefinition:
        clone = copy.copy(self)
        clone._timeline = self.timeline.transform_colors(color_transform)

        return clone

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> TextDefinition:
        return modifier.apply_on_text(self)

    def _place_glyphs(self) -> Timeline:
        assert self._extractor is not None
        fonts = self._extractor.fonts
        glyphs: dict[tuple[int, int, Color], ShapeDefinition] = {}
        objects: dict[int, FrameObject] = {}

        # A record only states what changes: the font, the color and the pen carry over.
        font = None
        height = 0
        color = Color(0, 0, 0)
        x = y = 0

        for record in self.tag.text_records:
            if record.font_id is not None:
                font = fonts.get(record.font_id)
                height = record.height or 0

            if record.color is not None:
                color = record.color

            if record.x_offset is not None:
                x = record.x_offset

            if record.y_offset is not None:
                y = record.y_offset

            for entry in record.glyphs:
                if font is not None and entry.glyph_index < len(font.glyphs):
                    key = (font.id, entry.glyph_index, color)

                    if key not in glyphs:
                        glyphs[key] = font.glyph(entry.glyph_index, color, self._extractor)

                    scale = height / font.em_square
                    matrix = self.tag.text_matrix @ Matrix(scale, scale, translate_x=x, translate_y=y)
                    depth = len(objects) + 1
                    objects[depth] = FrameObject.place(depth, glyphs[key], matrix)

                x += entry.advance

        return Timeline(self.bounds, Frame(self.bounds, objects))
