"""Port of ArakneSwf's `tests/Parser/Structure/Tag/EnableDebuggerTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.enable_debugger import EnableDebuggerTag


def test_read_v1():
    reader = Reader(b"my password\x00")
    tag = EnableDebuggerTag.read(reader, 1)

    assert tag.version == 1
    assert tag.password == b"my password"


def test_read_v2():
    reader = Reader(b"\x00\x00my password\x00")
    tag = EnableDebuggerTag.read(reader, 2)

    assert tag.version == 2
    assert tag.password == b"my password"
