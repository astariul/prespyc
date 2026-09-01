"""Port of ArakneSwf's DefineSoundTagTest."""

from __future__ import annotations

from prespyc.parser.structure.tag.define_sound import DefineSoundTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 5256)

    tag = DefineSoundTag.read(reader, 6807)

    assert tag.sound_id == 18
    assert tag.sound_format == 1
    assert tag.sound_rate == 0
    assert tag.is16_bits
    assert not tag.stereo
    assert tag.sound_sample_count == 4104
    assert len(tag.sound_data) == 1544
