"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ImportAssetsTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.import_assets import ImportAssetsTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "ground.swf"), 27)
    tag = ImportAssetsTag.read(reader, 1)

    assert tag.version == 1
    assert tag.url == b"clips/gfx/g1.swf"
    assert tag.characters == {1: b"[Link_g1-ground]"}


def test_read_v2():
    reader = Reader(b"my/path/to/assets.swf\x00\x01\x00\x03\x00\x02\x00Foo\x00\x03\x00Bar\x00\x04\x00Baz\x00")
    tag = ImportAssetsTag.read(reader, 2)

    assert tag.version == 2
    assert tag.url == b"my/path/to/assets.swf"
    assert tag.characters == {2: b"Foo", 3: b"Bar", 4: b"Baz"}
