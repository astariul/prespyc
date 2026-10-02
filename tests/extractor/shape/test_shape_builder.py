"""`ShapeBuilder`: drawing a shape character from scratch."""

from __future__ import annotations

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.shape.shape_builder import ShapeBuilder
from prespyc.extractor.shape.shape_definition import ShapeDefinition
from prespyc.extractor.shape.shape_processor import ShapeProcessor
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.line_style import LineStyle
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord
from prespyc.parser.structure.tag.define_shape import DefineShapeTag
from prespyc.swf_file import SwfFile
from tests.support import fixture

RED = FillStyle(FillStyle.SOLID, color=Color(255, 0, 0))


def _extractor():
    return SwfFile(fixture("extractor", "1047", "1047.swf")).extractor


def test_build_a_filled_polygon() -> None:
    shape = (
        ShapeBuilder(_extractor())
        .fill(RED)
        .move_to(0, 0)
        .line_to(200, 0)
        .line_to(200, 100)
        .line_to(0, 100)
        .line_to(0, 0)
        .build(1000)
    )

    image = Converter().to_image(shape)

    assert shape.id == 1000
    assert shape.bounds == Rectangle(0, 200, 0, 100)
    assert image.size == (10, 5)
    assert image.getpixel((5, 2)) == (255, 0, 0, 255)


def test_bounds_hold_curves_and_strokes() -> None:
    # The curve peaks at y = 100, halfway; the stroke adds half its width all around.
    shape = ShapeBuilder(_extractor()).line(LineStyle(40, Color(0, 0, 0))).move_to(0, 0).curve_to(100, 200, 200, 0)

    assert shape.build(1001).bounds == Rectangle(-20, 220, -20, 120)


def test_draws_like_the_tag_it_stands_for() -> None:
    extractor = _extractor()
    records = [
        StyleChangeRecord(False, False, False, True, True, -570, -1, 0, 1, 0, [], []),
        StraightEdgeRecord(True, False, 561, 289),
        StraightEdgeRecord(True, False, 561, -289),
        StraightEdgeRecord(True, False, -561, -287),
        StraightEdgeRecord(True, False, -561, 287),
        EndShapeRecord(),
    ]
    tag = DefineShapeTag(3, 63, Rectangle(-570, 552, -288, 288), ShapeWithStyle([RED], [], records))
    by_hand = ShapeDefinition(ShapeProcessor(extractor), 63, tag)

    built = (
        ShapeBuilder(extractor)
        .fill(RED)
        .move_to(-570, -1)
        .line_to(-9, 288)
        .line_to(552, -1)
        .line_to(-9, -288)
        .line_to(-570, -1)
        .build(63)
    )

    assert built.bounds == by_hand.bounds
    assert built.to_svg() == by_hand.to_svg()
