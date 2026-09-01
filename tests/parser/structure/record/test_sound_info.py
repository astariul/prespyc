"""Port of ArakneSwf's SoundInfoTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.sound_envelope import SoundEnvelope
from prespyc.parser.structure.record.sound_info import SoundInfo
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("extractor", "swf1", "new_theater.swf"), 14020)

    assert SoundInfo.read(reader) == SoundInfo(
        sync_stop=False,
        sync_no_multiple=False,
        in_point=None,
        out_point=None,
        loop_count=None,
        envelopes=[
            SoundEnvelope(pos44=1638, left_level=32768, right_level=32768),
            SoundEnvelope(pos44=2185, left_level=0, right_level=0),
        ],
    )


def test_read_empty():
    reader = Reader(b"\x00")

    assert SoundInfo.read(reader) == SoundInfo(
        sync_stop=False,
        sync_no_multiple=False,
        in_point=None,
        out_point=None,
        loop_count=None,
        envelopes=[],
    )


def test_read_all_flags():
    reader = Reader(b"\x3f\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x00")

    assert SoundInfo.read(reader) == SoundInfo(
        sync_stop=True,
        sync_no_multiple=True,
        in_point=67305985,
        out_point=134678021,
        loop_count=2569,
        envelopes=[],
    )
