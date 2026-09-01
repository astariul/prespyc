"""Port of ArakneSwf's SoundStreamBlockTagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.sound_stream_block import SoundStreamBlockTag


def test_read():
    reader = Reader(b"my sound data")

    tag = SoundStreamBlockTag.read(reader, reader.end)

    assert tag.sound_data == b"my sound data"
