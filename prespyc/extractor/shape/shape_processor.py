"""Turning define shape tags into shape objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.errors import Errors, ProcessingInvalidDataError
from prespyc.extractor.shape.edge import CurvedEdge, StraightEdge
from prespyc.extractor.shape.fill_type.bitmap import Bitmap
from prespyc.extractor.shape.fill_type.gradient import LinearGradient, RadialGradient
from prespyc.extractor.shape.fill_type.solid import Solid
from prespyc.extractor.shape.path_style import PathStyle
from prespyc.extractor.shape.paths_builder import PathsBuilder
from prespyc.extractor.shape.shape import Shape
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord

if TYPE_CHECKING:
    from prespyc.extractor.extractor import Extractor
    from prespyc.extractor.shape.edge import Edge
    from prespyc.extractor.shape.fill_type.fill_type import FillType
    from prespyc.extractor.shape.path import Path
    from prespyc.parser.structure.record.gradient import Gradient
    from prespyc.parser.structure.record.shape.line_style import LineStyle
    from prespyc.parser.structure.record.shape.shape_record import ShapeRecord
    from prespyc.parser.structure.tag.define_shape import DefineShapeTag
    from prespyc.parser.structure.tag.define_shape4 import DefineShape4Tag


class ShapeProcessor:
    """Processes define shape tags to create shape objects."""

    __slots__ = ("_extractor",)

    def __init__(self, extractor: Extractor) -> None:
        self._extractor = extractor

    def process(self, tag: DefineShapeTag | DefineShape4Tag) -> Shape:
        """Transform a `DefineShapeTag` or a `DefineShape4Tag` into a `Shape`."""
        return Shape(
            width=tag.shape_bounds.width,
            height=tag.shape_bounds.height,
            x_offset=-tag.shape_bounds.xmin,
            y_offset=-tag.shape_bounds.ymin,
            paths=self.process_records(
                tag.shapes.shape_records,
                tag.shapes.fill_styles,
                tag.shapes.line_styles,
            ),
        )

    def process_records(
        self,
        records: list[ShapeRecord],
        fill_styles: list[FillStyle],
        line_styles: list[LineStyle],
        ignore_zero_with_line: bool = True,
    ) -> list[Path]:
        """
        Process shape edge records to create paths.

        `ignore_zero_with_line` drops line styles with a zero width.
        """
        x = 0
        y = 0

        fill_style0: PathStyle | None = None
        fill_style1: PathStyle | None = None
        line_style: PathStyle | None = None

        # Style group counter to create unique style IDs when styles are changed
        style_group = 0

        builder = PathsBuilder()
        edges: list[Edge] = []

        for shape in records:
            if isinstance(shape, StyleChangeRecord):
                builder.merge(*edges)
                edges = []

                if shape.reset:
                    # Start a new drawing context
                    builder.finalize()

                if shape.state_new_styles:
                    # Reset styles to ensure that we don't use old styles
                    builder.close()

                    fill_styles = shape.fill_styles
                    line_styles = shape.line_styles
                    style_group += 1

                if shape.state_line_style:
                    style = _style_at(line_styles, shape.line_style - 1)
                    if style is not None and (style.width >= 1 or not ignore_zero_with_line):
                        line_style = PathStyle(
                            line_color=style.color,
                            line_fill=self._create_fill_type(style.fill_type) if style.fill_type is not None else None,
                            line_width=style.width,
                            id=f"L-{style_group}-{shape.line_style}",
                        )
                    else:
                        line_style = None

                if shape.state_fill_style0:
                    style = _style_at(fill_styles, shape.fill_style0 - 1)
                    if style is not None:
                        fill_style0 = PathStyle(
                            fill=self._create_fill_type(style),
                            reverse=True,
                            id=f"F-{style_group}-{shape.fill_style0}",
                        )
                    else:
                        fill_style0 = None

                if shape.state_fill_style1:
                    style = _style_at(fill_styles, shape.fill_style1 - 1)
                    if style is not None:
                        fill_style1 = PathStyle(
                            fill=self._create_fill_type(style),
                            id=f"F-{style_group}-{shape.fill_style1}",
                        )
                    else:
                        fill_style1 = None

                builder.set_active_styles(fill_style0, fill_style1, line_style)

                if shape.state_move_to:
                    x = shape.move_delta_x
                    y = shape.move_delta_y

            elif isinstance(shape, StraightEdgeRecord):
                to_x = x + shape.delta_x
                to_y = y + shape.delta_y

                edges.append(StraightEdge(x, y, to_x, to_y))

                x = to_x
                y = to_y

            elif isinstance(shape, CurvedEdgeRecord):
                from_x = x
                from_y = y
                control_x = x + shape.control_delta_x
                control_y = y + shape.control_delta_y
                to_x = x + shape.control_delta_x + shape.anchor_delta_x
                to_y = y + shape.control_delta_y + shape.anchor_delta_y

                edges.append(CurvedEdge(from_x, from_y, control_x, control_y, to_x, to_y))

                x = to_x
                y = to_y

            elif isinstance(shape, EndShapeRecord):
                builder.merge(*edges)

                return builder.export()

        return builder.export()

    def _create_fill_type(self, style: FillStyle) -> FillType:
        match style.type:
            case FillStyle.SOLID:
                return self._create_solid_fill(style)
            case FillStyle.LINEAR_GRADIENT:
                return self._create_linear_gradient_fill(style)
            case FillStyle.RADIAL_GRADIENT:
                return self._create_radial_gradient_fill(style, style.gradient)
            case FillStyle.FOCAL_GRADIENT:
                return self._create_radial_gradient_fill(style, style.focal_gradient)
            case FillStyle.REPEATING_BITMAP:
                return self._create_bitmap_fill(style, smoothed=True, repeat=True)
            case FillStyle.CLIPPED_BITMAP:
                return self._create_bitmap_fill(style, smoothed=True, repeat=False)
            case FillStyle.NON_SMOOTHED_REPEATING_BITMAP:
                return self._create_bitmap_fill(style, smoothed=False, repeat=True)
            case FillStyle.NON_SMOOTHED_CLIPPED_BITMAP:
                return self._create_bitmap_fill(style, smoothed=False, repeat=False)
            case _:
                if self._extractor.error_enabled(Errors.UNPROCESSABLE_DATA):
                    raise ProcessingInvalidDataError(f"Unknown fill style: {style.type}")

                return Solid(Color(0, 0, 0, 0))

    def _create_solid_fill(self, style: FillStyle) -> Solid:
        color = style.color
        assert color is not None

        return Solid(color)

    def _create_linear_gradient_fill(self, style: FillStyle) -> LinearGradient:
        matrix = style.matrix
        gradient = style.gradient

        assert matrix is not None and gradient is not None

        return LinearGradient(matrix, gradient)

    def _create_radial_gradient_fill(self, style: FillStyle, gradient: Gradient | None) -> RadialGradient:
        matrix = style.matrix

        assert matrix is not None
        assert gradient is not None

        return RadialGradient(matrix, gradient)

    def _create_bitmap_fill(self, style: FillStyle, smoothed: bool, repeat: bool) -> Bitmap:
        # Imported here so that the image package stays out of this module's import graph, as
        # `fill_type/bitmap.py` does for `TransformedImage`.
        from prespyc.extractor.image.empty_image import EmptyImage
        from prespyc.extractor.image.image_character import ImageCharacter

        bitmap_id = style.bitmap_id
        matrix = style.bitmap_matrix

        assert bitmap_id is not None and matrix is not None

        character = self._extractor.character(bitmap_id)

        if not isinstance(character, ImageCharacter):
            if self._extractor.error_enabled(Errors.UNPROCESSABLE_DATA):
                raise ProcessingInvalidDataError(f"The character {bitmap_id} is not a valid image character")

            character = EmptyImage(bitmap_id)

        return Bitmap(character, matrix, smoothed=smoothed, repeat=repeat)


def _style_at(styles: list[FillStyle] | list[LineStyle], index: int) -> FillStyle | LineStyle | None:
    """
    The style at `index`, or `None` when out of range.

    PHP's `$styles[$i] ?? null` yields null for a negative index; Python would wrap around.
    """
    if 0 <= index < len(styles):
        return styles[index]

    return None
