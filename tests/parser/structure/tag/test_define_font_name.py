"""Port of ArakneSwf's DefineFontNameTagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_font_name import DefineFontNameTag


def test_read():
    reader = Reader(b"\x35\x00Font name\x00Font copyright\x00")

    tag = DefineFontNameTag.read(reader)

    assert tag.font_id == 53
    assert tag.font_name == b"Font name"
    assert tag.font_copyright == b"Font copyright"
