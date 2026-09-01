"""Port of ArakneSwf's tests/Extractor/Timeline/TimelineProcessorTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.errors import Errors, ProcessingInvalidDataError
from prespyc.extractor.extractor import Extractor
from prespyc.extractor.sprite.sprite_definition import SpriteDefinition
from prespyc.extractor.timeline.timeline import Timeline
from prespyc.extractor.timeline.timeline_processor import TimelineProcessor
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_shape import DefineShapeTag
from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag
from prespyc.parser.structure.tag.end import EndTag
from prespyc.parser.structure.tag.place_object import PlaceObjectTag
from prespyc.parser.structure.tag.place_object2 import PlaceObject2Tag
from prespyc.parser.structure.tag.protect import ProtectTag
from prespyc.parser.structure.tag.show_frame import ShowFrameTag
from tests.support import SwfBuilder

# `Extractor.character()` builds the image characters before anything else, so a character cannot
# be resolved until they are ported.
requires_characters = pytest.mark.skipif(
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

# A 1x1 twip square outline, red, no fill.
#   0b0001_0000 0b1000_1000                             - bounds [0-1]x[0-1]
#   0b001001_00 0b000_1_11_00 0b00_1_01_01_0            - style record + line style + move to
#                                                         (0 bits) + line style 1, then an edge
#                                                         record + straight + 0 bits + general line
#                                                         + deltaX 1 + deltaY 1
_SHAPE = (
    b"\x01\x00\x10\x88"
    b"\x00"  # no fill
    b"\x01\x01\x00\xff\x00\x00"  # line style: 1px, red
    b"\x01"  # numFillBits = 0, numLineBits = 1
    b"\x24\x1c\x2a\x00"
)


def _sprite_swf(builder: SwfBuilder, sprite_tags, errors: int = Errors.ALL):
    """A SWF holding shape 1 and sprite 2, the sprite running `sprite_tags`."""
    return builder.create_swf_file(
        [
            (DefineShapeTag.TYPE_V1, _SHAPE),
            (DefineSpriteTag.TYPE, b"\x02\x00\x01\x00" + builder.build_tags(sprite_tags)),
        ],
        errors=errors,
    )


@requires_characters
def test_unsupported_tag(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObjectTag.TYPE, b"\x01\x00\x01\x00\x00"),
            (ShowFrameTag.TYPE, b""),
            (ProtectTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ],
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)

    with pytest.raises(ProcessingInvalidDataError, match=r"^Invalid tag type ProtectTag in timeline$"):
        processor.process(sprite.tag.tags)


@requires_characters
def test_unsupported_tag_ignore_errors(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObjectTag.TYPE, b"\x01\x00\x01\x00\x00"),
            (ShowFrameTag.TYPE, b""),
            (ProtectTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ],
        errors=Errors.NONE,
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)
    timeline = processor.process(sprite.tag.tags)

    assert timeline.bounds == Rectangle(0, 1, 0, 1)
    assert len(timeline.frames) == 1
    assert len(timeline.frames[0].objects) == 1
    assert timeline.frames[0].objects[1].object is extractor.character(1)


def test_new_object_missing_character_id(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file(
        [
            (PlaceObject2Tag.TYPE, b"\x00\x01\x00"),
            (EndTag.TYPE, b""),
        ]
    )
    processor = TimelineProcessor(Extractor(swf))

    with pytest.raises(ProcessingInvalidDataError, match=r"^New object at depth 1 without characterId$"):
        processor.process(swf.tags())


def test_new_object_missing_character_id_ignore_error(swf_builder: SwfBuilder):
    swf = swf_builder.create_swf_file(
        [
            (PlaceObject2Tag.TYPE, b"\x00\x01\x00"),
            (ShowFrameTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ],
        errors=Errors.NONE,
    )
    processor = TimelineProcessor(Extractor(swf))
    timeline = processor.process(swf.tags())

    assert len(timeline.frames) == 1
    assert len(timeline.frames[0].objects) == 0


@requires_characters
def test_missing_show_frame_tag(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObjectTag.TYPE, b"\x01\x00\x01\x00\x00"),
            (EndTag.TYPE, b""),
        ],
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)

    with pytest.raises(
        ProcessingInvalidDataError,
        match=r"^No frames found in the timeline: ShowFrame tag is missing$",
    ):
        processor.process(sprite.tag.tags)


@requires_characters
def test_missing_show_frame_tag_ignore(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObjectTag.TYPE, b"\x01\x00\x01\x00\x00"),
            (EndTag.TYPE, b""),
        ],
        errors=Errors.NONE,
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)

    assert processor.process(sprite.tag.tags) == Timeline.empty()


@requires_characters
def test_move_depth_not_exists(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObject2Tag.TYPE, b"\x01\x02\x00"),
            (ShowFrameTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ],
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)

    with pytest.raises(
        ProcessingInvalidDataError,
        match=r"^Cannot modify object as depth 2: it was not found$",
    ):
        processor.process(sprite.tag.tags)


@requires_characters
def test_move_depth_not_exists_ignore_error(swf_builder: SwfBuilder):
    swf = _sprite_swf(
        swf_builder,
        [
            (PlaceObject2Tag.TYPE, b"\x01\x02\x00"),
            (ShowFrameTag.TYPE, b""),
            (EndTag.TYPE, b""),
        ],
        errors=Errors.NONE,
    )
    extractor = Extractor(swf)
    sprite = extractor.character(2)
    assert isinstance(sprite, SpriteDefinition)

    processor = TimelineProcessor(extractor)

    assert processor.process(sprite.tag.tags) == Timeline.empty()
