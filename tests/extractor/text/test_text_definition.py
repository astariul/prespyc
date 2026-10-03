"""Static texts, drawn with the glyphs of their fonts."""

from __future__ import annotations

import io

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import ScaleResizer
from prespyc.extractor.text.text_definition import TextDefinition
from prespyc.swf_file import SwfFile
from tests.support import assert_image_looks_like, fixture


def test_text_places_one_glyph_per_entry() -> None:
    text = SwfFile(fixture("parser", "Examples1.swf")).extractor.character(2)

    assert isinstance(text, TextDefinition)
    assert text.bounds == text.tag.text_bounds
    assert len(text.timeline.frames[0].objects) == sum(len(record.glyphs) for record in text.tag.text_records)


def test_text_looks_like_ffdec_draws_it() -> None:
    sprite = SwfFile(fixture("parser", "Examples1.swf")).extractor["LetterA"]  # a single static text

    buffer = io.BytesIO()
    Converter(ScaleResizer(2)).to_image(sprite).save(buffer, format="PNG")

    assert_image_looks_like(buffer.getvalue(), fixture("extractor", "text", "LetterA.png"), 0.01)
