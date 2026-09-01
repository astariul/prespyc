"""Port of ArakneSwf's `tests/Parser/Structure/Tag/DoABCTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.do_abc import DoABCTag


def test_read():
    reader = Reader(b"\x12\x34\x56\x78My script name\x00the ABC data")
    tag = DoABCTag.read(reader, 31)

    assert tag.flags == 0x78563412
    assert tag.name == b"My script name"
    assert tag.data == b"the ABC data"
