"""Phase 0 gate: the fixture tree is complete and the golden harness works."""

from __future__ import annotations

import pytest

from tests.support import FIXTURES, canonical_xml, fixture


def test_fixture_tree_is_complete():
    assert len(list(FIXTURES.rglob("*.swf"))) == 59
    assert len(list(FIXTURES.rglob("*.svg"))) == 1130
    assert fixture("extractor", "1047", "1047.swf").is_file()
    assert fixture("parser", "graphics.swf").is_file()


def test_canonical_xml_ignores_formatting_and_attribute_order():
    a = '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="1px" height="2px"><g id="a"/></svg>'
    b = (
        '<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" height="2px" width="1px">\n'
        '    <g id="a"/>\n</svg>\n'
    )

    assert canonical_xml(a) == canonical_xml(b)


def test_canonical_xml_keeps_values():
    a = '<svg width="1px"/>'
    b = '<svg width="2px"/>'

    assert canonical_xml(a) != canonical_xml(b)


def test_canonical_xml_keeps_text():
    assert canonical_xml("<a>x</a>") != canonical_xml("<a>y</a>")


@pytest.mark.parametrize("name", ["mask/189.svg", "1047/61_frames/frame_0.svg"])
def test_goldens_are_parseable(name):
    assert canonical_xml(fixture("extractor", *name.split("/")).read_bytes()).startswith("<{")
