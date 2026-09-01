"""Port of ArakneSwf's DefineFont4TagTest."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_font4 import DefineFont4Tag


def test_read():
    reader = Reader(b"\x21\x00\x05My font\x00my fond data")

    tag = DefineFont4Tag.read(reader, reader.end)

    assert tag.font_id == 33
    assert not tag.italic
    assert tag.bold
    assert tag.name == b"My font"
    assert tag.data == b"my fond data"
