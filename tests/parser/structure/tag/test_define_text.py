"""Port of ArakneSwf's DefineTextTagTest."""

from __future__ import annotations

import re

import pytest

from prespyc.errors import Errors, InvalidDataError
from prespyc.parser.reader import Reader
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_text import DefineTextTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 134)

    tag = DefineTextTag.read(reader, 1)

    assert tag.character_id == 2
    assert tag.text_bounds == Rectangle(xmin=0, xmax=808, ymin=74, ymax=563)
    assert tag.text_matrix == Matrix()
    assert tag.glyph_bits == 0
    assert tag.advance_bits == 10
    assert len(tag.text_records) == 1
    assert tag.text_records[0].font_id == 1
    assert tag.text_records[0].color == Color(0, 0, 0)
    assert tag.text_records[0].y_offset == 540
    assert tag.text_records[0].x_offset is None
    assert tag.text_records[0].height == 600
    assert len(tag.text_records[0].glyphs) == 1
    assert tag.text_records[0].glyphs[0].glyph_index == 0
    assert tag.text_records[0].glyphs[0].advance == 433


def test_read_invalid_glyph_bits():
    reader = Reader(b"\x01\x00\x00\x00\x80\x01\x00")

    with pytest.raises(
        InvalidDataError, match=re.escape("Glyph bits (128) or advance bits (1) are out of bounds (0-32)")
    ):
        DefineTextTag.read(reader, 1)


def test_read_invalid_advance_bits():
    reader = Reader(b"\x01\x00\x00\x00\x01\x80\x00")

    with pytest.raises(
        InvalidDataError, match=re.escape("Glyph bits (1) or advance bits (128) are out of bounds (0-32)")
    ):
        DefineTextTag.read(reader, 1)


def test_read_invalid_glyph_and_advance_bits_ignore_error():
    reader = Reader(b"\x01\x00\x00\x00\x80\x80\x00", errors=Errors.NONE)

    tag = DefineTextTag.read(reader, 1)

    assert tag.version == 1
    assert tag.character_id == 1
    assert tag.glyph_bits == 128
    assert tag.advance_bits == 128
    assert len(tag.text_records) == 0
