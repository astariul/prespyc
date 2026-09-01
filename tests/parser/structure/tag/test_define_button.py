"""Port of ArakneSwf's DefineButtonTagTest."""

from __future__ import annotations

from prespyc.parser.structure.action.opcode import Opcode
from prespyc.parser.structure.record.button_record import ButtonRecord
from prespyc.parser.structure.tag.define_button import DefineButtonTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 5198)

    tag = DefineButtonTag.read(reader, 5250)

    assert tag.button_id == 17
    assert len(tag.characters) == 4
    assert all(isinstance(character, ButtonRecord) for character in tag.characters)
    assert tag.characters[0].character_id == 15
    assert tag.characters[1].character_id == 16
    assert tag.characters[2].character_id == 15
    assert tag.characters[3].character_id == 15
    assert len(tag.actions) == 1
    assert tag.actions[0].opcode == Opcode.NULL
