"""Port of ArakneSwf's `tests/Extractor/MorphShape/MorphShapeDefinitionTest.php`."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas
from prespyc.extractor.morph_shape.morph_shape import MorphShape
from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture


def test_getters():
    swf = SwfFile(fixture("extractor", "homestuck", "00004.swf"))
    morph_shape = swf.asset_by_id(63)
    assert isinstance(morph_shape, MorphShapeDefinition)

    assert morph_shape.frames_count() == 1
    assert morph_shape.frames_count(True) == 1
    assert morph_shape.id == 63
    assert morph_shape.tag.character_id == 63
    assert morph_shape.bounds == Rectangle(-470, 2201, -1440, 344)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (0, Rectangle(-470, 2201, -1440, 344)),
        (12547, Rectangle(-470, 2174, -1440, 344)),
        (32000, Rectangle(-470, 2132, -1442, 344)),
        (MorphShape.MAX_RATIO, Rectangle(-470, 2061, -1445, 344)),
    ],
)
def test_bounds_with_ratio(ratio: int, expected: Rectangle):
    swf = SwfFile(fixture("extractor", "homestuck", "00004.swf"))
    morph_shape = swf.asset_by_id(63)

    assert morph_shape.with_ratio(ratio).bounds == expected


@pytest.mark.parametrize(
    ("ratio", "golden"),
    [
        (0, "morphshape_63_frame1.svg"),
        (10000, "morphshape_63_frame10000.svg"),
        (20000, "morphshape_63_frame20000.svg"),
        (30000, "morphshape_63_frame30000.svg"),
        (40000, "morphshape_63_frame40000.svg"),
        (50000, "morphshape_63_frame50000.svg"),
        (65535, "morphshape_63_last_frame.svg"),
    ],
)
def test_draw_with_ratio(ratio: int, golden: str):
    swf = SwfFile(fixture("extractor", "homestuck", "00004.swf"))
    morph_shape = swf.asset_by_id(63)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(ratio)

    assert_svg_matches(
        morph_shape.draw(SvgCanvas(morph_shape.bounds)).render(),
        fixture("extractor", "homestuck", golden),
    )


@pytest.mark.parametrize("ratio", range(0, 65537, 4096))
def test_morph_shape_with_morph_style(ratio: int):
    swf = SwfFile(fixture("extractor", "morphshape", "morphshape.swf"))
    morph_shape = swf.asset_by_id(1)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(ratio)
    svg = morph_shape.draw(SvgCanvas(morph_shape.bounds)).render()

    assert_svg_matches(svg, fixture("extractor", "morphshape", f"morphshape_frame{ratio}.svg"))


def test_transform_colors():
    swf = SwfFile(fixture("extractor", "morphshape", "morphshape.swf"))
    morph_shape = swf.asset_by_id(1)

    morph_shape = morph_shape.with_ratio(25000)
    transformed = morph_shape.transform_colors(ColorTransform(red_mult=512, green_mult=128, blue_mult=0))

    assert morph_shape != transformed
    assert_svg_matches(
        transformed.draw(SvgCanvas(morph_shape.bounds)).render(),
        fixture("extractor", "morphshape", "morphshape_frame25000_transformed.svg"),
    )


def test_modify():
    swf = SwfFile(fixture("extractor", "morphshape", "morphshape.swf"))
    morph_shape = swf.asset_by_id(1)
    transformed = morph_shape.transform_colors(ColorTransform(red_mult=512, green_mult=128, blue_mult=0))

    modifier = Mock()
    modifier.apply_on_morph_shape.return_value = transformed

    assert morph_shape.modify(modifier) is transformed
    modifier.apply_on_morph_shape.assert_called_once_with(morph_shape)


@pytest.mark.parametrize("ratio", range(0, 65537, 16384))
def test_with_gradient_fixed(ratio: int):
    swf = SwfFile(fixture("extractor", "1615", "1615.swf"))
    morph_shape = swf.asset_by_id(222)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(ratio)
    svg = morph_shape.draw(SvgCanvas(morph_shape.bounds)).render()

    assert_svg_matches(svg, fixture("extractor", "1615", "222", f"{ratio}.svg"))


@pytest.mark.parametrize("ratio", range(0, 65537, 16384))
def test_with_gradient_dynamic(ratio: int):
    swf = SwfFile(fixture("extractor", "1520", "1520.swf"))
    morph_shape = swf.asset_by_id(47)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(ratio)
    svg = morph_shape.draw(SvgCanvas(morph_shape.bounds)).render()

    assert_svg_matches(svg, fixture("extractor", "1520", "47", f"{ratio}.svg"))
