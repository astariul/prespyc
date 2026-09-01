"""Port of ArakneSwf's DefineEditTextTagTest."""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.tag.define_edit_text import DefineEditTextTag
from tests.support import fixture, fixture_reader


def test_read():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 4822)

    tag = DefineEditTextTag.read(reader)

    assert tag.character_id == 19
    assert tag.bounds == Rectangle(xmin=-40, xmax=1320, ymin=-40, ymax=431)
    assert tag.border
    assert tag.font_height == 280
    assert not tag.word_wrap
    assert not tag.multiline
    assert not tag.password
    assert not tag.read_only
    assert not tag.auto_size
    assert not tag.no_select
    assert not tag.was_static
    assert not tag.use_outlines
    assert tag.font_id == 1
    assert tag.text_color == Color(0, 0, 0, 255)
    assert tag.layout.align == 0
    assert tag.layout.left_margin == 0
    assert tag.layout.right_margin == 0
    assert tag.layout.indent == 0
    assert tag.layout.leading == 40
    assert tag.variable_name == b""
