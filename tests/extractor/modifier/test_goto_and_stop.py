"""Port of ArakneSwf's tests/Extractor/Modifier/GotoAndStopTest.php."""

from __future__ import annotations

from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.goto_and_stop import GotoAndStop
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture


def test_with_label():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    sprite = extractor.by_name("staticR")
    new_sprite = sprite.modify(GotoAndStop("static"))

    assert new_sprite.frames_count(True) == 1
    assert new_sprite.timeline.frames[0].objects[1].object.timeline.frames[0].label == "static"


def test_with_number():
    swf = SwfFile(fixture("extractor", "1047", "1047.swf"))
    extractor = Extractor(swf)

    sprite = extractor.by_name("staticR")
    new_sprite = sprite.modify(GotoAndStop(3))

    assert new_sprite.frames_count(True) == 1
    assert_svg_matches(new_sprite.to_svg(), fixture("extractor", "1047", "staticR-2.svg"))
