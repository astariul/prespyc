"""Port of ArakneSwf's `tests/Parser/Structure/Tag/ReflexTagTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.tag.reflex import ReflexTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "alignment_fr_147.swf"), 18)
    tag = ReflexTag.read(reader, 21)

    assert tag.name == b"rfx"
