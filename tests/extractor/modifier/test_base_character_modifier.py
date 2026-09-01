"""Port of ArakneSwf's tests/Extractor/Modifier/AbstractCharacterModifierTest.php."""

from __future__ import annotations

from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier
from prespyc.swf_file import SwfFile
from tests.support import fixture


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
