"""
Translated from ArakneSwf's `tests/Extractor/SwfExtractorTest.php`.

This is the primary fidelity gate: most of the ~1,130 golden SVGs are asserted from here.
"""

from __future__ import annotations

import pytest

from prespyc.errors import Errors
from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas
from prespyc.extractor.image.image_bits_definition import ImageBitsDefinition
from prespyc.extractor.image.jpeg_image_definition import JpegImageDefinition
from prespyc.extractor.image.lossless_image_definition import LosslessImageDefinition
from prespyc.extractor.missing_character import MissingCharacter
from prespyc.extractor.morph_shape.morph_shape import MorphShape
from prespyc.extractor.morph_shape.morph_shape_definition import MorphShapeDefinition
from prespyc.extractor.shape.shape_definition import ShapeDefinition
from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_shape import DefineShapeTag
from prespyc.swf_file import SwfFile
from tests.support import assert_image_matches, assert_svg_equals, assert_svg_matches, fixture


def extractor(*parts: str, errors: int = Errors.ALL):
    return SwfFile(fixture("extractor", *parts), errors=errors).extractor


def test_shapes():
    shapes = extractor("2.swf").shapes

    assert len(shapes) == 2
    assert list(shapes) == [1, 2]
    assert all(isinstance(shape, ShapeDefinition) for shape in shapes.values())

    assert shapes[1].id == 1
    assert shapes[1].frames_count() == 1
    assert shapes[1].frames_count(True) == 1
    assert isinstance(shapes[1].tag, DefineShapeTag)
    assert shapes[2].id == 2
    assert shapes[2].frames_count() == 1
    assert shapes[2].frames_count(True) == 1
    assert isinstance(shapes[2].tag, DefineShapeTag)

    assert_svg_matches(shapes[1].to_svg(), fixture("extractor", "2.svg"))
    assert_svg_equals(
        shapes[2].to_svg(),
        """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="25.3px" height="4.8px">
            <g transform="matrix(1, 0, 0, 1, -0.05, 0)">
                <path fill="#000000" stroke="none" fill-rule="evenodd" d="M25.35 2.4Q25.3 3.4 21.6 4.1L12.7 4.8L3.75 4.1Q0 3.4 0.05 2.4Q0 1.4 3.75 0.7L12.7 0L21.6 0.7Q25.3 1.4 25.35 2.4"/>
            </g>
        </svg>""",
    )

    # The processed shape is cached, so the same instance comes back
    assert shapes[1].shape is shapes[1].shape
    assert shapes[2].shape is shapes[2].shape


def test_shapes_without_subpixel_stroke():
    shapes = extractor("2.swf").shapes

    assert len(shapes) == 2

    assert_svg_matches(shapes[1].to_svg(subpixel_stroke_width=False), fixture("extractor", "2-no-sp-stroke.svg"))
    assert_svg_equals(
        shapes[2].to_svg(subpixel_stroke_width=False),
        """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="25.3px" height="4.8px">
            <g transform="matrix(1, 0, 0, 1, -0.05, 0)">
                <path fill="#000000" stroke="none" fill-rule="evenodd" d="M25.35 2.4Q25.3 3.4 21.6 4.1L12.7 4.8L3.75 4.1Q0 3.4 0.05 2.4Q0 1.4 3.75 0.7L12.7 0L21.6 0.7Q25.3 1.4 25.35 2.4"/>
            </g>
        </svg>""",
    )


def test_sprites():
    for sprite in extractor("complex_sprite.swf").sprites.values():
        assert_svg_matches(sprite.to_svg(), fixture("extractor", f"sprite-{sprite.id}.svg"))


def test_character_not_found():
    ex = extractor("complex_sprite.swf")

    assert isinstance(ex.character(10000), MissingCharacter)
    assert ex.character(10000).frames_count() == 1
    assert ex.character(10000).frames_count(True) == 1

    drawer = SvgCanvas(Rectangle(0, 0, 0, 0))
    assert ex.character(10000).draw(drawer) is drawer

    assert_svg_equals(
        drawer.render(),
        '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" height="0px" width="0px"/>',
    )


def test_character_0_is_the_timeline():
    ex = extractor("complex_sprite.swf")

    assert ex.timeline() == ex.character(0)


def test_images():
    ex = extractor("maps", "0.swf")
    images = ex.images

    assert len(images) == 72

    types = {type(image) for image in images.values()}
    assert ImageBitsDefinition in types
    assert JpegImageDefinition in types
    assert LosslessImageDefinition in types

    assert_image_matches(images[507].to_png(), fixture("extractor", "maps", "jpeg-507.png"))
    assert_image_matches(images[525].to_jpeg(), fixture("extractor", "maps", "jpeg-525.jpg"))
    assert_image_matches(ex.character(525).to_jpeg(), fixture("extractor", "maps", "jpeg-525.jpg"))


def test_sprite_with_raster_image():
    sprite = extractor("mob-leponge", "mob-leponge.swf").character(29)
    assert_svg_matches(sprite.to_svg(), fixture("extractor", "mob-leponge", "sprite-29.svg"))

    sprite = extractor("1597", "1597.swf").character(48)
    assert_svg_matches(sprite.to_svg(), fixture("extractor", "1597", "sprite-48.svg"))


def test_sprite_with_raster_image_and_color_transform():
    ex = extractor("1047", "1047.swf")

    assert_svg_matches(ex.character(3).to_svg(), fixture("extractor", "1047", "sprite-3.svg"))
    assert_svg_matches(ex.character(29).to_svg(), fixture("extractor", "1047", "sprite-29.svg"))


def test_by_name():
    ex = extractor("1047", "1047.swf")

    static_r = ex.by_name("staticR")
    assert isinstance(static_r, SpriteDefinition)
    assert static_r.id == 66
    assert_svg_matches(static_r.to_svg(), fixture("extractor", "1047", "staticR.svg"))

    static_l = ex["staticL"]
    assert isinstance(static_l, SpriteDefinition)
    assert static_l.id == 68
    assert_svg_matches(static_l.to_svg(), fixture("extractor", "1047", "staticL.svg"))


def test_sprite_with_multiple_frames():
    sprite = extractor("1047", "1047.swf").character(61)

    assert sprite.frames_count() == 40
    assert sprite.frames_count(True) == 40

    for frame in range(40):
        assert_svg_matches(sprite.to_svg(frame), fixture("extractor", "1047", "61_frames", f"frame_{frame}.svg"))


def test_sprite_with_multiple_frames_recursively():
    sprite = extractor("1047", "1047.swf").by_name("anim0R")

    assert sprite.frames_count() == 1
    assert sprite.frames_count(True) == 40

    for frame in range(40):
        assert_svg_matches(sprite.to_svg(frame), fixture("extractor", "1047", "anim0R", f"frame_{frame}.svg"))


def test_sprite_with_actions():
    sprite = extractor("1047", "1047.swf").character(5)

    assert len(sprite.timeline.frames[0].actions) == 1
    assert len(sprite.timeline.frames[0].actions[0].actions) == 16


def test_exported():
    assert extractor("1047", "1047.swf").exported == {
        "runR": 29,
        "runL": 43,
        "bonusR": 53,
        "bonusL": 56,
        "anim0R": 62,
        "anim0L": 64,
        "staticR": 66,
        "staticL": 68,
        "walkL": 70,
        "walkR": 72,
        "anim1R": 77,
        "anim1L": 79,
        "hitR": 91,
        "hitL": 95,
        "dieR": 97,
        "dieL": 99,
    }


def test_timeline_single_frame():
    timeline = extractor("1", "1.swf").timeline(False)

    for frame, svg in enumerate(timeline.to_svg_all()):
        assert_svg_matches(svg, fixture("extractor", "1", f"frame_{frame}.svg"))


def test_timeline_multiple_frames():
    timeline = extractor("homestuck", "00004.swf").timeline()

    for frame, svg in enumerate(timeline.to_svg_all()):
        assert_svg_matches(svg, fixture("extractor", "homestuck", "timeline", f"frame_{frame}.svg"))


def test_timeline_with_morph_shapes():
    timeline = extractor("1001", "1001.swf").timeline(False)

    for frame in range(timeline.frames_count(True)):
        assert_svg_matches(timeline.to_svg(frame), fixture("extractor", "1001", f"frame_{frame}.svg"))


def test_color_transform_is_applied_lazily():
    sprite = extractor("1305", "1305.swf").by_name("anim0R")

    assert_svg_matches(sprite.to_svg(), fixture("extractor", "1305", "anim0R.svg"))


def test_with_place_object3_filters():
    timeline = extractor("62", "62.swf").timeline(False)

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "62", "timeline.svg"))


def test_with_drop_shadow_filter():
    timeline = extractor("54", "54.swf").timeline(False)

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "54", "timeline.svg"))


def test_bitmap_transformed_multiple_times():
    timeline = extractor("60", "60.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "60", "timeline.svg"))


def test_zero_size_sprite_when_last_frame_is_empty():
    sprite = extractor("1058", "1058.swf").by_name("anim0R")

    assert sprite.bounds == Rectangle(-817, 1430, -2299, 816)
    assert_svg_matches(sprite.to_svg(), fixture("extractor", "1058", "anim0R.svg"))


def test_move_with_new_character():
    sprite = extractor("1601", "1601.swf").by_name("anim0R")
    assert isinstance(sprite, SpriteDefinition)

    assert_svg_matches(sprite.to_svg(17), fixture("extractor", "1601", "anim0R", "17.svg"))
    assert_svg_matches(sprite.to_svg(18), fixture("extractor", "1601", "anim0R", "18.svg"))

    inner = sprite.timeline.frames[0].objects[1].object
    frame17 = inner.timeline.frames[17].objects[86]
    frame18 = inner.timeline.frames[18].objects[86]

    assert frame17.matrix.scale_x == frame18.matrix.scale_x
    assert frame17.matrix.scale_y == frame18.matrix.scale_y
    assert frame17.matrix.rotate_skew0 == frame18.matrix.rotate_skew0
    assert frame17.matrix.rotate_skew1 == frame18.matrix.rotate_skew1
    assert frame17.matrix.translate_x == pytest.approx(frame18.matrix.translate_x, abs=100)
    assert frame17.matrix.translate_y == pytest.approx(frame18.matrix.translate_y, abs=100)
    assert frame17.object.id == 118
    assert frame18.object.id == 119


def test_ignore_frame_object_with_too_high_bounds():
    sprite = extractor("1435", "1435.swf").by_name("anim0R")

    assert_svg_matches(sprite.to_svg(23), fixture("extractor", "1435", "anim0R.svg"))
    assert sprite.bounds.width == int(48.45 * 20)
    assert sprite.bounds.height == int(35.95 * 20)


def test_swf1_file_with_place_object():
    timeline = extractor("swf1", "new_theater.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "swf1", "new_theater_frame0.svg"))


def test_with_single_clip_depth():
    timeline = extractor("mask", "189.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "mask", "189.svg"))


def test_with_clip_depth_on_sprite():
    timeline = extractor("mask", "sprite_mask.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "mask", "sprite_mask.svg"))


@pytest.mark.parametrize("name", ["nested_masks", "nested_masks2"])
def test_with_nested_clip_depth(name):
    timeline = extractor("mask", f"{name}.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "mask", f"{name}.svg"))


def test_blur_filter_too_high():
    timeline = extractor("filters", "146.swf").timeline()

    assert_svg_matches(timeline.to_svg(), fixture("extractor", "filters", "146.svg"))


def test_release_if_out_of_memory():
    ex = extractor("filters", "146.swf")
    ex.character(1)
    assert ex._characters

    assert ex.release_if_out_of_memory(1_000_000_000) is False
    assert ex._characters

    assert ex.release_if_out_of_memory(1000) is True
    assert not ex._characters


def test_color_transform_on_transparent_pixel_is_ignored():
    sprite = extractor("o3", "o3.swf").character(31)

    assert isinstance(sprite, SpriteDefinition)
    assert_svg_matches(sprite.to_svg(), fixture("extractor", "o3", "sprite-31.svg"))


def test_swf9_symbol_class_export():
    ex = extractor("swf9", "149.swf")

    assert len(ex.exported) == 1
    assert "149_fla.MainTimeline" in ex.exported
    assert ex.exported["149_fla.MainTimeline"] == 0
    assert ex.character(0) == ex.by_name("149_fla.MainTimeline")


def test_morph_shapes():
    ex = extractor("homestuck", "00004.swf")
    morph_shapes = ex.morph_shapes

    assert len(morph_shapes) == 6
    assert all(isinstance(m, MorphShapeDefinition) for m in morph_shapes.values())
    assert list(morph_shapes) == [55, 57, 63, 67, 69, 72]

    assert ex.morph_shapes is morph_shapes


def test_morph_shape_corrupted():
    ex = extractor("1008", "1008.swf", errors=Errors.NONE)

    morph_shape = ex.character(43)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(12000)
    assert_svg_equals(
        morph_shape.draw(SvgCanvas(morph_shape.bounds)).render(),
        '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" width="0px" height="0px">'
        '<g transform="matrix(1, 0, 0, 1, 0, 0)"/></svg>',
    )

    for character_id in (32, 59):
        morph_shape = ex.character(character_id)

        for ratio in range(0, 65537, 8192):
            morph_shape = morph_shape.with_ratio(ratio)
            svg = morph_shape.draw(SvgCanvas(morph_shape.bounds)).render()

            assert_svg_matches(svg, fixture("extractor", "1008", str(character_id), f"{ratio}.svg"))

    for character_id in (64, 90):
        sprite = ex.character(character_id)

        for frame, svg in enumerate(sprite.timeline.to_svg_all()):
            assert_svg_matches(svg, fixture("extractor", "1008", str(character_id), f"{frame}.svg"))


def test_morph_shape_with_zero_width_line_start():
    ex = extractor("morphshape", "a3.swf", errors=Errors.NONE)

    morph_shape = ex.character(569)
    assert isinstance(morph_shape, MorphShapeDefinition)

    morph_shape = morph_shape.with_ratio(42000)
    svg = morph_shape.draw(SvgCanvas(morph_shape.bounds, subpixel_stroke_width=False)).render()
    assert_svg_matches(svg, fixture("extractor", "morphshape", "a3", "569-42000.svg"))

    morph_shape = morph_shape.with_ratio(MorphShape.MAX_RATIO)
    svg = morph_shape.draw(SvgCanvas(morph_shape.bounds, subpixel_stroke_width=False)).render()
    assert_svg_matches(svg, fixture("extractor", "morphshape", "a3", "569-65535.svg"))
