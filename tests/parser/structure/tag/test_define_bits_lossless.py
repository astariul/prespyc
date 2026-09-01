"""Port of ArakneSwf's `DefineBitsLosslessTagTest`."""

from __future__ import annotations

import re
import zlib

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.tag.define_bits_lossless import DefineBitsLosslessTag


def test_read_invalid_image_format():
    reader = Reader(b"\x01\x00\x42\x01\x01" + zlib.compress(b"pixels data"))

    with pytest.raises(
        InvalidDataError,
        match=re.escape("Invalid bitmap format 66 for DefineBitsLossless tag (version 1)"),
    ):
        DefineBitsLosslessTag.read(reader, 1, reader.end)


def test_read_invalid_image_format_ignore_error():
    reader = Reader(b"\x01\x00\x42\x01\x00\x01\x00" + zlib.compress(b"pixels data"), errors=Errors.NONE)
    tag = DefineBitsLosslessTag.read(reader, 1, reader.end)

    assert tag.version == 1
    assert tag.bitmap_format == 66
    assert tag.character_id == 1
    assert tag.bitmap_width == 1
    assert tag.bitmap_height == 1
    assert tag.color_table is None
    assert tag.pixel_data == b"pixels data"
