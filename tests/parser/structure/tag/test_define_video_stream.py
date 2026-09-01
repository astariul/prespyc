"""Port of ArakneSwf's DefineVideoStreamTagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_video_stream import DefineVideoStreamTag


def test_read():
    reader = Reader(b"\x29\x00\x0c\x00\x40\x01\xf0\x00\x05\x02")

    tag = DefineVideoStreamTag.read(reader)

    assert tag.character_id == 41
    assert tag.num_frames == 12
    assert tag.width == 320
    assert tag.height == 240
    assert tag.deblocking == 2
    assert tag.smoothing
    assert tag.codec_id == 2
