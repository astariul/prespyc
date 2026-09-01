"""Port of ArakneSwf's SoundStreamHeadTagTest."""

from __future__ import annotations

from prespyc.parser.structure.tag.sound_stream_head import SoundStreamHeadTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "1131.swf"), 1633)

    tag = SoundStreamHeadTag.read(reader, 2)

    assert tag.version == 2
    assert tag.playback_sound_rate == 1
    assert tag.playback_sound_size == 1
    assert tag.playback_sound_type == 0
    assert tag.stream_sound_compression == 0
    assert tag.stream_sound_rate == 0
    assert tag.stream_sound_size == 0
    assert tag.stream_sound_sample_count == 0
