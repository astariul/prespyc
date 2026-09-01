"""Port of ArakneSwf's VideoFrameTagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.video_frame import VideoFrameTag


def test_read():
    reader = Reader(b"\x12\x00\x64\x00video data")

    tag = VideoFrameTag.read(reader, 14)

    assert tag.stream_id == 18
    assert tag.frame_num == 100
    assert tag.video_data == b"video data"
