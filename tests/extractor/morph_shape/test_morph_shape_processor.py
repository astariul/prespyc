"""Port of ArakneSwf's `tests/Extractor/MorphShape/MorphShapeProcessorTest.php`."""

from __future__ import annotations

from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas
from prespyc.extractor.extractor import Extractor
from prespyc.extractor.morph_shape.morph_shape_processor import MorphShapeProcessor
from prespyc.parser.structure.tag.define_morph_shape import DefineMorphShapeTag
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_matches, fixture


def test_process_end_records_too_small():
    swf = SwfFile(fixture("extractor", "homestuck", "00004.swf"))
    tag = swf.asset_by_id(63).tag
    corrupted_tag = DefineMorphShapeTag(
        tag.character_id,
        tag.start_bounds,
        tag.end_bounds,
        tag.offset,
        tag.fill_styles,
        tag.line_styles,
        tag.start_edges,
        tag.end_edges[0:10],
    )

    processor = MorphShapeProcessor(Extractor(swf))
    morph_shape = processor.process(corrupted_tag)
    shape = morph_shape.interpolate(32768)

    assert len(shape.paths) == 2
    assert len(shape.paths[0].edges) == 9
    assert len(shape.paths[1].edges) == 9

    renderer = SvgCanvas(tag.start_bounds)
    renderer.shape(shape)

    assert_svg_matches(
        renderer.render(),
        fixture("extractor", "homestuck", "morphshape_corrupted_too_small_end.svg"),
    )
