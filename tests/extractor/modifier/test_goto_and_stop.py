"""Port of ArakneSwf's tests/Extractor/Modifier/GotoAndStopTest.php."""

from __future__ import annotations

import importlib.util

import pytest

from prespyc.extractor.extractor import Extractor
from prespyc.extractor.modifier.goto_and_stop import GotoAndStop
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture

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
