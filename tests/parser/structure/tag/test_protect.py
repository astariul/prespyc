"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ProtectTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.protect import ProtectTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("sunAndShadow.swf"), 32)
    tag = ProtectTag.read(reader, 32)

    assert tag.password is None


def test_read_with_password():
    reader = Reader(b"My password\x00")
    tag = ProtectTag.read(reader, reader.end)

    assert tag.password == b"My password"
