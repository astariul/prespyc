"""
Translated from ArakneSwf's `ConverterTest.php`, plus `ScaleResizerTest::functionalWithConverter`.

Only the SVG and WEBP paths exist here: PNG, GIF, JPEG and animated output are dropped.
"""

from __future__ import annotations

import io

from PIL import Image

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import FitSizeResizer, ScaleResizer
from prespyc.swf_file import SwfFile
from tests.support import assert_image_looks_like, assert_svg_matches, fixture


def drawable_65():
    return SwfFile(fixture("extractor", "1047", "1047.swf")).extractor.character(65)


def test_to_svg_simple():
    svg = Converter().to_svg(drawable_65(), 5)

    assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", "65-5.svg"))


def test_to_svg_with_resize():
    svg = Converter(FitSizeResizer(128, 128)).to_svg(drawable_65(), 5)

    assert_svg_matches(svg, fixture("extractor", "1047", "65_frames", "65-5@128.svg"))


def test_to_svg_with_scale_resizer():
    sprite = SwfFile(fixture("extractor", "mob-leponge", "mob-leponge.swf")).extractor.by_name("staticR")
    svg = Converter(ScaleResizer(1.2), subpixel_stroke_width=False).to_svg(sprite)

    assert_svg_matches(svg, fixture("extractor", "mob-leponge", "staticRx1.2.svg"))


def test_to_webp_simple():
    webp = Converter().to_webp(drawable_65(), 5, lossless=True)

    with Image.open(io.BytesIO(webp)) as image:
        assert image.format == "WEBP"
        assert image.size == (40, 42)


def test_to_webp_with_size():
    webp = Converter(FitSizeResizer(128, 128)).to_webp(drawable_65(), 5, lossless=True)

    with Image.open(io.BytesIO(webp)) as image:
        assert image.format == "WEBP"
        assert image.size == (121, 128)

    # ArakneSwf ships one golden per renderer, because Imagick's native SVG support and librsvg
    # disagree; resvg is closest to the librsvg one. The remaining difference is antialiasing on the
    # edges: 2 pixels out of 15488 differ by more than 32/255.
    assert_image_looks_like(webp, fixture("extractor", "1047", "65_frames", "65-5-rsvg@128.webp"), delta=0.005)


def test_empty_drawable_gives_a_transparent_pixel():
    from prespyc.extractor.missing_character import MissingCharacter

    image = Converter(ScaleResizer(2)).to_image(MissingCharacter(1))

    assert image.size == (1, 1)
    assert image.getpixel((0, 0)) == (0, 0, 0, 0)


def test_empty_drawable_fills_the_size_asked_for():
    from prespyc.extractor.timeline.timeline import Timeline

    assert Converter(FitSizeResizer(128, 64)).to_image(Timeline.empty()).size == (128, 64)


def test_empty_drawable_to_webp():
    from prespyc.extractor.timeline.timeline import Timeline

    webp = Converter().to_webp(Timeline.empty())

    assert Image.open(io.BytesIO(webp)).size == (1, 1)


def _hairline(scale: float):
    """A 1 twip wide stroke, placed by a sprite with `scale`."""
    from prespyc.extractor.shape.shape_builder import ShapeBuilder
    from prespyc.extractor.timeline.timeline import Timeline
    from prespyc.parser.structure.record.color import Color
    from prespyc.parser.structure.record.matrix import Matrix
    from prespyc.parser.structure.record.shape.line_style import LineStyle

    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor
    line = ShapeBuilder(extractor).line(LineStyle(1, Color(0, 0, 0))).move_to(0, 0).line_to(400, 400).build(1000)

    return Timeline.sequence(line, tag_matrix=Matrix(scale_x=scale, scale_y=scale))


def _stroke_width(svg: str) -> float:
    import re

    return float(re.search(r'stroke-width="([0-9.]+)"', svg).group(1))


def test_minimum_stroke_width_is_one_output_pixel():
    # 1px of the output is 1 / (2 * 0.5) user units under the zoom and the placement.
    svg = Converter(ScaleResizer(2), subpixel_stroke_width=False).to_svg(_hairline(0.5))

    assert _stroke_width(svg) == 1.0
    assert "vector-effect" not in svg


def test_minimum_stroke_width_follows_the_placement_scale():
    svg = Converter(ScaleResizer(2), subpixel_stroke_width=False).to_svg(_hairline(4.0))

    assert _stroke_width(svg) == 0.125


def test_subpixel_stroke_width_keeps_the_real_width():
    svg = Converter(ScaleResizer(2)).to_svg(_hairline(4.0))

    assert _stroke_width(svg) == 0.05
