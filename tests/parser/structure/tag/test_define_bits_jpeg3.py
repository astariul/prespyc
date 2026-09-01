"""Port of ArakneSwf's `DefineBitsJPEG3TagTest`."""

from __future__ import annotations

import re
import zlib

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.image_data_type import ImageDataType
from prespyc.parser.structure.tag.define_bits_jpeg3 import DefineBitsJPEG3Tag
from tests.parser.structure.tag.test_define_bits_jpeg2 import SMALL_GIF, SMALL_JPEG, SMALL_PNG


def test_read_jpeg():
    reader = Reader(b"\x21\x00\x7d\x00\x00\x00" + SMALL_JPEG + zlib.compress(b"\x80"))
    tag = DefineBitsJPEG3Tag.read(reader, reader.end)

    assert tag.character_id == 33
    assert tag.image_data == SMALL_JPEG
    assert tag.type == ImageDataType.JPEG
    assert tag.alpha_data == b"\x80"


def test_read_jpeg_invalid_zlib_alpha_data():
    reader = Reader(b"\x21\x00\x7d\x00\x00\x00" + SMALL_JPEG + b"invalid zlib data")

    # PHP reports the gzuncompress() reason; Python reports the zlib one, so only the prefix
    # is asserted verbatim.
    with pytest.raises(InvalidDataError, match=re.escape("Invalid compressed data at offset 148: ")):
        DefineBitsJPEG3Tag.read(reader, reader.end)


def test_read_jpeg_invalid_zlib_alpha_data_ignore_error():
    reader = Reader(b"\x21\x00\x7d\x00\x00\x00" + SMALL_JPEG + b"invalid zlib data", errors=Errors.NONE)
    tag = DefineBitsJPEG3Tag.read(reader, reader.end)

    assert tag.character_id == 33
    assert tag.image_data == SMALL_JPEG
    assert tag.type == ImageDataType.JPEG
    assert tag.alpha_data is None


def test_read_png():
    reader = Reader(b"\x21\x00\x43\x00\x00\x00" + SMALL_PNG)
    tag = DefineBitsJPEG3Tag.read(reader, reader.end)

    assert tag.character_id == 33
    assert tag.image_data == SMALL_PNG
    assert tag.type == ImageDataType.PNG
    assert tag.alpha_data is None


def test_read_gif():
    reader = Reader(b"\x21\x00\x2b\x00\x00\x00" + SMALL_GIF)
    tag = DefineBitsJPEG3Tag.read(reader, reader.end)

    assert tag.character_id == 33
    assert tag.image_data == SMALL_GIF
    assert tag.type == ImageDataType.GIF89A
    assert tag.alpha_data is None
