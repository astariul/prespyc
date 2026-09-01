"""Translated from ArakneSwf's `tests/Extractor/Shape/ShapeToSvgFunctionalTest.php`."""

from __future__ import annotations

import pytest

from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas
from prespyc.extractor.shape.shape_processor import ShapeProcessor
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture


@pytest.mark.parametrize(("swf", "svg"), [("shape.swf", "shape.svg"), ("2.swf", "2.svg")])
def test_single_shape(swf, svg):
    file = SwfFile(fixture("extractor", swf))
    processor = ShapeProcessor(file.extractor)

    for _, tag in file.tags(2, 22, 32, 83):
        shape = processor.process(tag)
        canvas = SvgCanvas(tag.shape_bounds)
        canvas.shape(shape)

        assert_svg_matches(canvas.to_xml(), fixture("extractor", svg))

        return

    pytest.fail("no shape tag found")


@pytest.mark.parametrize(
    ("swf", "character_id", "golden"),
    [
        (("complex_sprite.swf",), 11, ("shape_with_transparency.svg",)),
        (("complex_sprite.swf",), 1, ("shape_with_radial_gradient.svg",)),
        (("complex_sprite.swf",), 8, ("shape_with_complex_fill.svg",)),
        (("mob-leponge", "mob-leponge.swf"), 2, ("mob-leponge", "shadow.svg")),
        (("1597", "1597.swf"), 2, ("1597", "shadow.svg")),
        (("7022", "7022.swf"), 5, ("7022", "5.svg")),
        (("1700", "1700.swf"), 203, ("1700", "shape-203.svg")),
    ],
)
def test_shape_to_svg(swf, character_id, golden):
    shape = SwfFile(fixture("extractor", *swf)).extractor.character(character_id)

    assert_svg_matches(shape.to_svg(), fixture("extractor", *golden))


@pytest.mark.parametrize("character_id", [1, 5, 6, 8, 12, 13])
def test_define_shape4(character_id):
    shape = SwfFile(fixture("extractor", "62", "62.swf")).extractor.character(character_id)

    assert_svg_matches(shape.to_svg(), fixture("extractor", "62", f"shape-{character_id}.svg"))
