"""Port of ArakneSwf's StartSound2TagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.sound_info import SoundInfo
from prespyc.parser.structure.tag.start_sound2 import StartSound2Tag


def test_read():
    reader = Reader(b"Sound class name\x00\x3f\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x00")

    tag = StartSound2Tag.read(reader)

    assert tag.sound_class_name == b"Sound class name"
    assert tag.sound_info == SoundInfo(
        sync_stop=True,
        sync_no_multiple=True,
        in_point=67305985,
        out_point=134678021,
        loop_count=2569,
        envelopes=[],
    )
