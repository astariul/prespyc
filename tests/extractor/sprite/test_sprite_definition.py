"""Port of ArakneSwf's tests/Extractor/Sprite/SpriteDefinitionTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.errors import CircularReferenceError, Errors
from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier
from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.place_object import PlaceObjectTag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from prespyc.swf_file import SwfFile
from tests.support import SwfBuilder, assert_svg_matches, fixture

# `Extractor.character()` builds the image characters before anything else, so a character cannot
# be resolved until they are ported.
pytestmark = pytest.mark.skipif(
    any(
        importlib.util.find_spec(name) is None
        for name in (
            "prespyc.extractor.image.image_bits_definition",
            "prespyc.extractor.image.jpeg_image_definition",
            "prespyc.extractor.image.lossless_image_definition",
        )
    ),
    reason="the image characters are not ported yet, so Extractor.character() cannot resolve anything",
)


def _self_referencing_sprite(builder: SwfBuilder, sprite_id: int, placed_id: int) -> tuple[int, bytes]:
    """A sprite tag displaying character `placed_id` at depth 1 on a single frame."""
    body = sprite_id.to_bytes(2, "little") + b"\x01\x00"
    tags = builder.build_tags(
        [
            (PlaceObjectTag.TYPE, placed_id.to_bytes(2, "little") + b"\x01\x00\x00"),
            (ShowFrameTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ]
    )

    return (DefineSpriteTag.TYPE, body + tags)


def test_circular_reference(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file([_self_referencing_sprite(swf_builder, 1, 1)])
    sprite = swf.asset_by_id(1)

    assert isinstance(sprite, SpriteDefinition)

    with pytest.raises(
        CircularReferenceError,
        match=r"^Circular reference detected while processing sprite 1$",
    ):
        _ = sprite.timeline


def test_indirect_circular_reference(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file(
        [
            _self_referencing_sprite(swf_builder, 1, 2),
            _self_referencing_sprite(swf_builder, 2, 1),
        ]
    )
    sprite = swf.asset_by_id(1)

    assert isinstance(sprite, SpriteDefinition)

    with pytest.raises(
        CircularReferenceError,
        match=r"^Circular reference detected while processing sprite 1$",
    ):
        _ = sprite.timeline


def test_circular_reference_ignore_error(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file([_self_referencing_sprite(swf_builder, 1, 1)], errors=Errors.NONE)
    sprite = swf.asset_by_id(1)

    assert isinstance(sprite, SpriteDefinition)
    timeline = sprite.timeline

    assert len(timeline.frames) == 1
    assert not timeline.frames[0].objects
    assert not timeline.frames[0].actions


def test_indirect_circular_reference_ignore_error(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file(
        [
            _self_referencing_sprite(swf_builder, 1, 2),
            _self_referencing_sprite(swf_builder, 2, 1),
        ],
        errors=Errors.NONE,
    )
    sprite = swf.asset_by_id(1)

    assert isinstance(sprite, SpriteDefinition)
    timeline = sprite.timeline

    assert len(timeline.frames) == 1
    assert not timeline.frames[0].objects
    assert not timeline.frames[0].actions


def test_timeline_is_cached(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file([_self_referencing_sprite(swf_builder, 1, 1)], errors=Errors.NONE)
    sprite = swf.asset_by_id(1)

    assert sprite.timeline is sprite.timeline


def test_to_svg_without_subpixel_stroke_width():
    extractor = Extractor(SwfFile(fixture("extractor", "1305", "1305.swf")))
    sprite = extractor.by_name("anim0R")

    assert isinstance(sprite, SpriteDefinition)

    svg = sprite.to_svg(subpixel_stroke_width=False)
    assert_svg_matches(svg, fixture("extractor", "1305", "without-subpixel-stroke-width.svg"))


def test_with_attachment():
    sprite = SwfFile(fixture("extractor", "1305", "1305.swf")).asset_by_name("anim0R")
    other = SwfFile(fixture("extractor", "1", "1.swf")).timeline(False)

    combined = sprite.with_attachment(other, depth=10, name="attached")
    svg = combined.to_svg()

    assert_svg_matches(svg, fixture("extractor", "1305", "with-attachment.svg"))


def test_modify():
    sprite = SwfFile(fixture("extractor", "1047", "1047.swf")).asset_by_name("anim0R")

    class Modifier(BaseCharacterModifier):
        def apply_on_shape(self, shape):
            return shape.transform_colors(
                ColorTransform(
                    red_mult=0,
                    green_mult=0,
                    blue_mult=0,
                    alpha_mult=0,
                    red_add=255 if shape.id % 3 == 0 else 0,
                    green_add=255 if shape.id % 3 == 1 else 0,
                    blue_add=255 if shape.id % 3 == 2 else 0,
                    alpha_add=255,
                )
            )

        def apply_on_sprite(self, sprite: SpriteDefinition) -> SpriteDefinition:
            if sprite.id == 27:
                sprite = sprite.with_attachment(
                    SwfFile(fixture("extractor", "1435", "1435.swf")).asset_by_name("staticR"),
                    depth=100,
                    name="addedSprite",
                )

            return sprite

    sprite = sprite.modify(Modifier())

    svg = sprite.to_svg()
    assert_svg_matches(svg, fixture("extractor", "1047", "modified.svg"))


def test_modify_without_modification_should_return_same_instance():
    sprite = SwfFile(fixture("extractor", "1047", "1047.swf")).asset_by_name("anim0R")

    assert sprite.modify(BaseCharacterModifier()) is sprite
