"""Port of ArakneSwf's DefineSpriteTagTest."""

from __future__ import annotations

from prespyc.errors import Errors
from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_sprite import DefineSpriteTag
from prespyc.parser.swf import Swf
from tests.support import fixture


def test_read_ignore_invalid_tag():
    data = fixture("parser", "1131.swf").read_bytes()
    swf = Swf.read(Reader(data))
    tag = swf.dictionary[47]

    reader = Reader(data)
    reader.skip_bytes(8)
    content = bytearray(reader.uncompress().chunk(tag.offset, tag.offset + tag.length).read_bytes(tag.length))
    content[11] = 0x42
    content[65] = 0x42
    content[75] = 0x42
    content[202] = 0x00

    reader = Reader(bytes(content), errors=Errors.IGNORE_INVALID_TAG)
    tag = DefineSpriteTag.read(reader, 5, reader.end)

    assert len(tag.tags) == 11
