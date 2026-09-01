"""Port of ArakneSwf's `tests/Parser/Structure/Tag/SetTabIndexTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.set_tab_index import SetTabIndexTag


def test_read():
    reader = Reader(b"\x10\x00\x03\x00")
    tag = SetTabIndexTag.read(reader)

    assert tag.depth == 16
    assert tag.tab_index == 3
