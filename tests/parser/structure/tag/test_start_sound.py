"""Port of ArakneSwf's StartSoundTagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.sound_envelope import SoundEnvelope
from prespyc.parser.structure.record.sound_info import SoundInfo
from prespyc.parser.structure.tag.start_sound import StartSoundTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 7227)

    tag = StartSoundTag.read(reader)

    assert tag.sound_id == 18
    assert tag.sound_info == SoundInfo(
        sync_stop=False,
        sync_no_multiple=False,
        in_point=None,
        out_point=None,
        loop_count=None,
        envelopes=[SoundEnvelope(pos44=0, left_level=32768, right_level=0)],
    )
