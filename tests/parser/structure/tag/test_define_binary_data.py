"""Port of ArakneSwf's `tests/Parser/Structure/Tag/DefineBinaryDataTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_binary_data import DefineBinaryDataTag


def test_read():
    reader = Reader(b"\x14\x00\x00\x00\x00\x00binary data")
    tag = DefineBinaryDataTag.read(reader, 17)

    assert tag.tag == 20
    assert tag.data == b"binary data"
