"""Port of ArakneSwf's tests/Extractor/Modifier/AbstractCharacterModifierTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier
from prespyc.swf_file import SwfFile
from tests.support import fixture

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


def test_methods():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    modifier = BaseCharacterModifier()

    shape = extractor.character(36)
    assert modifier.apply_on_shape(shape) is shape

    sprite = extractor.character(65)
    assert modifier.apply_on_sprite(sprite) is sprite

    timeline = extractor.character(65).timeline
    assert modifier.apply_on_timeline(timeline) is timeline

    frame = timeline.frames[0]
    assert modifier.apply_on_frame(frame) is frame

    image = extractor.character(1)
    assert modifier.apply_on_image(image) is image

    swf = SwfFile(fixture("extractor", "morphshape", "morphshape.swf"))
    morph_shape = swf.asset_by_id(1)
    assert modifier.apply_on_morph_shape(morph_shape) is morph_shape
