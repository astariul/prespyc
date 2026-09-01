"""Port of ArakneSwf's DefineButtonSoundTagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.sound_info import SoundInfo
from prespyc.parser.structure.tag.define_button_sound import DefineButtonSoundTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 6813)

    tag = DefineButtonSoundTag.read(reader)

    assert tag.button_id == 17
    assert tag.button_sound_char0 == 0
    assert tag.button_sound_info0 is None
    assert tag.button_sound_char1 == 0
    assert tag.button_sound_info1 is None
    assert tag.button_sound_char2 == 18
    assert tag.button_sound_info2 == SoundInfo(
        sync_stop=False,
        sync_no_multiple=False,
        in_point=None,
        out_point=None,
        loop_count=None,
        envelopes=[],
    )
    assert tag.button_sound_char3 == 0
    assert tag.button_sound_info3 is None
