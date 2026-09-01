"""Port of ArakneSwf's `tests/Parser/Structure/SwfTagTest.php`."""

from __future__ import annotations

import re

import pytest

from prespyc.errors import Errors, ExtraDataError, UnknownTagError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.action.action_record import ActionRecord
from prespyc.parser.structure.raw_tag import RawTag
from prespyc.parser.structure.tag.unknown import UnknownTag
from tests.support import fixture, fixture_reader


def test_parse_unknown_tag():
    reader = Reader(b"\x11\x11my unparsed data!")
    tags = list(RawTag.read_all(reader))  # `iterator_to_array()` in PHP: the whole generator is consumed
    tag = tags[0]

    with pytest.raises(UnknownTagError, match=re.escape("Unknown tag with code 68 at offset 2")):
        tag.parse(reader, 5)


def test_parse_unknown_tag_ignore_error():
    reader = Reader(b"\x11\x11my unparsed data!", errors=Errors.NONE)
    tags = list(RawTag.read_all(reader))  # `iterator_to_array()` in PHP: the whole generator is consumed
    tag = tags[0]

    parsed = tag.parse(reader, 5)

    assert isinstance(parsed, UnknownTag)
    assert parsed.code == 68
    assert parsed.data == b"my unparsed data!"


def test_parse_with_remaining_data_error():
    reader = Reader(b"\x44\x00my unparsed data!")
    tags = list(RawTag.read_all(reader))  # `iterator_to_array()` in PHP: the whole generator is consumed
    tag = tags[0]

    with pytest.raises(ExtraDataError, match=re.escape("Extra data found after tag 1 at offset 2 (length = 4)")):
        tag.parse(reader, 5)


def test_parse_tag_invalid_length_ignore_error():
    reader = Reader(b"\x3f\x03\x78\x9a\xbc\xde\x12\x34\x56\x78", errors=Errors.NONE)
    tags = list(RawTag.read_all(reader))  # `iterator_to_array()` in PHP: the whole generator is consumed
    tag = tags[0]

    parsed = tag.parse(reader, 5)

    assert all(isinstance(action, ActionRecord) for action in parsed.actions)
    assert len(parsed.actions) == 2


@pytest.mark.parametrize("path", [fixture("extractor", "core", "core.swf")], ids=["core.swf"])
def test_coverage(path):
    """Every tag of a real file must resolve to a named tag structure, never to `UnknownTag`."""
    reader = fixture_reader(path, 21, errors=Errors.ALL & ~Errors.EXTRA_DATA)

    for tag in RawTag.read_all(reader):
        assert isinstance(tag, RawTag)

        # Ensure that the tag can be parsed
        parsed = tag.parse(reader, 9)
        assert not isinstance(parsed, UnknownTag), f"Tag {tag.type} should not be unknown"

        cls = type(parsed)
        assert cls.__module__.startswith("prespyc.parser.structure.tag.")
        assert cls.__name__.endswith("Tag")
