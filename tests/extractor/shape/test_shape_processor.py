"""Port of `tests/Extractor/Shape/ShapeProcessorTest.php`."""

from __future__ import annotations

import pytest

from prespyc.errors import Errors, ProcessingInvalidDataError
from prespyc.extractor.extractor import Extractor
from prespyc.extractor.image.empty_image import EmptyImage
from prespyc.extractor.shape.fill_type.bitmap import Bitmap
from prespyc.extractor.shape.fill_type.solid import Solid
from prespyc.extractor.shape.path import Path
from prespyc.extractor.shape.shape_processor import ShapeProcessor
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle
from prespyc.parser.structure.record.shape.end_shape_record import EndShapeRecord
from prespyc.parser.structure.record.shape.fill_style import FillStyle
from prespyc.parser.structure.record.shape.shape_with_style import ShapeWithStyle
from prespyc.parser.structure.record.shape.straight_edge_record import StraightEdgeRecord
from prespyc.parser.structure.record.shape.style_change_record import StyleChangeRecord
from prespyc.parser.structure.tag.define_shape import DefineShapeTag
from prespyc.swf_file import SwfFile
from tests.support import fixture


def _square_tag(fill_style: FillStyle) -> DefineShapeTag:
    """A hand-built 1x1 twip square, filled with `fill_style`."""
    return DefineShapeTag(
        1,
        1,
        Rectangle(0, 1, 0, 1),
        ShapeWithStyle(
            fill_styles=[fill_style],
            line_styles=[],
            shape_records=[
                StyleChangeRecord(
                    state_new_styles=False,
                    state_line_style=False,
                    state_fill_style0=False,
                    state_fill_style1=True,
                    state_move_to=False,
                    move_delta_x=0,
                    move_delta_y=0,
                    fill_style0=0,
                    fill_style1=1,
                    line_style=0,
                    fill_styles=[],
                    line_styles=[],
                ),
                StraightEdgeRecord(False, False, 1, 0),
                StraightEdgeRecord(False, True, 0, 1),
                StraightEdgeRecord(False, False, -1, 0),
                StraightEdgeRecord(False, True, 0, -1),
                EndShapeRecord(),
            ],
        ),
    )


def test_process():
    swf = SwfFile(fixture("extractor", "shape.swf"))
    processor = ShapeProcessor(Extractor(swf))
    _, tag = next(iter(swf.tags(DefineShapeTag.TYPE_V2)))

    shape = processor.process(tag)

    assert shape.width == 940
    assert shape.height == 960
    assert shape.x_offset == -5034
    assert shape.y_offset == -3519
    assert len(shape.paths) == 33
    assert all(isinstance(path, Path) for path in shape.paths)


def test_process_with_invalid_fill_style():
    swf = SwfFile(fixture("extractor", "shape.swf"))
    processor = ShapeProcessor(Extractor(swf))
    tag = _square_tag(FillStyle(type=5))

    with pytest.raises(ProcessingInvalidDataError, match="Unknown fill style: 5"):
        processor.process(tag)


def test_process_with_invalid_fill_style_ignore():
    swf = SwfFile(fixture("extractor", "shape.swf"), errors=Errors.NONE)
    processor = ShapeProcessor(Extractor(swf))
    tag = _square_tag(FillStyle(type=5))

    shape = processor.process(tag)

    assert len(shape.paths) == 1
    assert shape.paths[0].style.fill == Solid(Color(0, 0, 0, 0))


def test_process_with_invalid_bitmap():
    swf = SwfFile(fixture("extractor", "shape.swf"))
    processor = ShapeProcessor(Extractor(swf))
    tag = _square_tag(FillStyle(type=FillStyle.CLIPPED_BITMAP, bitmap_id=404, bitmap_matrix=Matrix()))

    with pytest.raises(ProcessingInvalidDataError, match="The character 404 is not a valid image character"):
        processor.process(tag)


def test_process_with_invalid_bitmap_ignore_error():
    swf = SwfFile(fixture("extractor", "shape.swf"), errors=Errors.NONE)
    processor = ShapeProcessor(Extractor(swf))
    tag = _square_tag(FillStyle(type=FillStyle.CLIPPED_BITMAP, bitmap_id=404, bitmap_matrix=Matrix()))

    shape = processor.process(tag)

    assert len(shape.paths) == 1
    assert shape.paths[0].style.fill == Bitmap(bitmap=EmptyImage(404), matrix=Matrix())
