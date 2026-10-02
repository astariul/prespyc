"""Buttons, drawn in their up state."""

from __future__ import annotations

from prespyc.extractor.button.button_definition import ButtonDefinition
from prespyc.extractor.drawer.converter import Converter
from prespyc.swf_file import SwfFile
from tests.support import fixture


def test_button_draws_its_up_state() -> None:
    extractor = SwfFile(fixture("extractor", "swf1", "new_theater.swf")).extractor

    button = extractor.character(17)  # up: character 15; over, down and hit test: 16, 15, 15

    assert isinstance(button, ButtonDefinition)
    [placed] = button.timeline.frames[0].objects.values()
    assert placed.object is extractor.character(15)
    assert button.bounds == placed.bounds


def test_sprite_draws_the_button_it_places() -> None:
    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor
    sprite = extractor[51]  # frames 4 to 8 show button 50 alone

    placed = sprite.timeline.frames[3].objects[1]

    assert isinstance(placed.object, ButtonDefinition)
    assert sprite.bounds.union(placed.bounds) == sprite.bounds
    assert Converter().to_image(sprite, 3).getbbox() is not None
