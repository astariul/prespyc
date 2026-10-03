"""Drawing a shape character from scratch."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Self

from prespyc.extractor.shape.shape_definition import ShapeDefinition
from prespyc.extractor.shape.shape_processor import ShapeProcessor
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.curved_edge_record import CurvedEdgeRecord
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord
from prespyc.parser.structure.tag.define_shape import DefineShapeTag

if TYPE_CHECKING:
    from prespyc.extractor.extractor import Extractor
    from prespyc.parser.structure.record.shape.fill_style import FillStyle
    from prespyc.parser.structure.record.shape.line_style import LineStyle


class ShapeBuilder:
    """
    Draws a shape the way a DefineShape tag describes one: pick the fill and the line, move, then
    draw edges. Coordinates are in twips and absolute.

    ```python
    tile = (
        ShapeBuilder(swf.extractor)
        .fill(FillStyle(FillStyle.REPEATING_BITMAP, bitmap_id=62, bitmap_matrix=Matrix(20.0, 20.0)))
        .move_to(-570, -1)
        .line_to(-9, 288)
        .line_to(552, -1)
        .line_to(-9, -288)
        .line_to(-570, -1)
        .build(63)
    )
    ```

    The extractor resolves the bitmaps the fills refer to.
    """

    __slots__ = ("_extractor", "_fill_styles", "_line_styles", "_line_width", "_points", "_records", "_x", "_y")

    def __init__(self, extractor: Extractor) -> None:
        self._extractor = extractor
        self._fill_styles: list[FillStyle] = []
        self._line_styles: list[LineStyle] = []
        self._records: list[StyleChangeRecord | StraightEdgeRecord | CurvedEdgeRecord] = []
        self._points: list[tuple[float, float]] = []
        self._line_width = 0
        """Widest stroke drawn so far, in twips."""
        self._x = 0
        self._y = 0

    def fill(self, style: FillStyle | None) -> Self:
        """Fill the next edges with `style`, or not at all with `None`."""
        if style is not None:
            self._fill_styles.append(style)

        index = len(self._fill_styles) if style is not None else 0
        self._records.append(_style_change(state_fill_style1=True, fill_style1=index))

        return self

    def line(self, style: LineStyle | None) -> Self:
        """Stroke the next edges with `style`, or not at all with `None`."""
        if style is not None:
            self._line_styles.append(style)
            self._line_width = max(self._line_width, style.width)

        index = len(self._line_styles) if style is not None else 0
        self._records.append(_style_change(state_line_style=True, line_style=index))

        return self

    def move_to(self, x: int, y: int) -> Self:
        """Move the pen to `(x, y)` without drawing."""
        self._records.append(_style_change(state_move_to=True, move_delta_x=x, move_delta_y=y))
        self._x, self._y = x, y

        return self

    def line_to(self, x: int, y: int) -> Self:
        """Draw a straight edge to `(x, y)`."""
        self._records.append(StraightEdgeRecord(True, False, x - self._x, y - self._y))
        self._points += [(self._x, self._y), (x, y)]
        self._x, self._y = x, y

        return self

    def curve_to(self, control_x: int, control_y: int, x: int, y: int) -> Self:
        """Draw a quadratic curve to `(x, y)`, bent towards the control point."""
        self._records.append(CurvedEdgeRecord(control_x - self._x, control_y - self._y, x - control_x, y - control_y))
        self._points += [(self._x, self._y), (x, y), *_extremums(self._x, self._y, control_x, control_y, x, y)]
        self._x, self._y = x, y

        return self

    def build(self, id: int, bounds: Rectangle | None = None) -> ShapeDefinition:
        """
        The shape, as character `id`.

        `bounds` defaults to what the edges cover, plus half the widest stroke all around.
        """
        if bounds is None:
            bounds = self._bounds()

        tag = DefineShapeTag(
            version=3,
            shape_id=id,
            shape_bounds=bounds,
            shapes=ShapeWithStyle(self._fill_styles, self._line_styles, [*self._records, EndShapeRecord()]),
        )

        return ShapeDefinition(ShapeProcessor(self._extractor), id, tag)

    def _bounds(self) -> Rectangle:
        if not self._points:
            return Rectangle(0, 0, 0, 0)

        margin = self._line_width / 2
        xs = [x for x, _ in self._points]
        ys = [y for _, y in self._points]

        return Rectangle(
            math.floor(min(xs) - margin),
            math.ceil(max(xs) + margin),
            math.floor(min(ys) - margin),
            math.ceil(max(ys) + margin),
        )


def _style_change(
    state_line_style: bool = False,
    state_fill_style1: bool = False,
    state_move_to: bool = False,
    move_delta_x: int = 0,
    move_delta_y: int = 0,
    fill_style1: int = 0,
    line_style: int = 0,
) -> StyleChangeRecord:
    return StyleChangeRecord(
        state_new_styles=False,
        state_line_style=state_line_style,
        state_fill_style0=False,
        state_fill_style1=state_fill_style1,
        state_move_to=state_move_to,
        move_delta_x=move_delta_x,
        move_delta_y=move_delta_y,
        fill_style0=0,
        fill_style1=fill_style1,
        line_style=line_style,
        fill_styles=[],
        line_styles=[],
    )


def _extremums(x0: int, y0: int, cx: int, cy: int, x1: int, y1: int) -> list[tuple[float, float]]:
    """The points where a quadratic curve turns back, on either axis."""
    points = []

    for a, b, c in ((x0, cx, x1), (y0, cy, y1)):
        denominator = a - 2 * b + c

        if denominator == 0:
            continue

        t = (a - b) / denominator

        if 0 < t < 1:
            points.append(
                (
                    (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1,
                    (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1,
                )
            )

    return points
