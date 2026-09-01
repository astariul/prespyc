"""Port of ArakneSwf's `tests/Parser/Structure/Tag/MetadataTagTest.php`."""

from __future__ import annotations

from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.metadata import MetadataTag


def test_read():
    reader = Reader(b"my metadata\x00")
    tag = MetadataTag.read(reader)

    assert tag.metadata == b"my metadata"
