"""The room filters spread over, around what they filter."""

from __future__ import annotations

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.shape.shape_builder import ShapeBuilder
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.output.exporter import build_spritesheet
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.filter.blur_filter import BlurFilter
from prespyc.parser.structure.record.filter.drop_shadow_filter import DropShadowFilter
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.swf_file import SwfFile
from tests.support import fixture


def _blurred_square() -> Timeline:
    """A 10x10 px square, blurred by 4.5 px horizontally and 2 px vertically."""
    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor
    square = (
        ShapeBuilder(extractor)
        .fill(FillStyle(FillStyle.SOLID, color=Color(255, 0, 0)))
        .move_to(0, 0)
        .line_to(200, 0)
        .line_to(200, 200)
        .line_to(0, 200)
        .line_to(0, 0)
        .build(1000)
    )
    placed = FrameObject.place(1, square, filters=[BlurFilter(blur_x=4.5, blur_y=2.0, passes=1)])

    return Timeline(placed.bounds, Frame(placed.bounds, {1: placed}))


def test_filter_spread():
    shadow = DropShadowFilter(Color(0, 0, 0), 2.0, 3.0, 0.0, 5.0, 1.0, False, False, False, 1)

    assert BlurFilter(blur_x=4.5, blur_y=2.0, passes=1).spread() == (4.5, 2.0)
    assert shadow.spread() == (7.0, 3.0)


def test_room_is_the_widest_filter_of_the_tree_in_whole_pixels():
    blurred = _blurred_square()
    parent = Timeline.sequence(blurred)

    assert blurred.filter_room == (100, 40)
    assert parent.filter_room == (100, 40)


def test_converter_pads_the_canvas_with_the_room():
    blurred = _blurred_square()
    converter = Converter()

    image = converter.to_image(blurred)

    assert converter.canvas_bounds(blurred) == Rectangle(-100, 300, -40, 240)
    red, _, _, alpha = image.getpixel((10, 7))

    assert image.size == (20, 14)
    assert red > 200 and alpha > 200


def test_converter_renders_the_bounds_it_is_given():
    blurred = _blurred_square()

    image = Converter().to_image(blurred, bounds=Rectangle(-200, 400, -200, 400))

    red, _, _, alpha = image.getpixel((15, 15))

    assert image.size == (30, 30)
    assert red > 200 and alpha > 200


def test_spritesheet_anchor_holds_the_room():
    sheet = build_spritesheet(_blurred_square(), "blurred")

    assert sheet.bounds == (-5.0, -2.0, 15.0, 12.0)
