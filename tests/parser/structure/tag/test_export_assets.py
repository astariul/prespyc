"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ExportAssetsTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.export_assets import ExportAssetsTag


def test_read():
    reader = Reader(b"\x03\x00\x42\x00test 1\x00\x43\x00test 2\x00\x44\x00test 3\x00")
    tag = ExportAssetsTag.read(reader)

    assert tag.characters == {66: b"test 1", 67: b"test 2", 68: b"test 3"}


def test_read_should_stop_at_end_of_tag():
    reader = Reader(b"\x15\x00\x42\x00test 1\x00\x43\x00test 2\x00\x44\x00test 3\x00")
    tag = ExportAssetsTag.read(reader)

    assert tag.characters == {66: b"test 1", 67: b"test 2", 68: b"test 3"}
