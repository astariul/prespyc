"""Port of `tests/Extractor/Shape/PathStyleTest.php`."""

from __future__ import annotations

from prespyc.extractor.shape.fill_type.solid import Solid
from prespyc.extractor.shape.path_style import PathStyle
from prespyc.parser.structure.record.color import Color


def test_hash():
    assert PathStyle(None, None, None, 0).hash == PathStyle(None, None, None, 0).hash
    assert (
        PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
        == PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
    )
    assert PathStyle(None, Color(125, 14, 0), None, 0).hash == PathStyle(None, Color(125, 14, 0), None, 0).hash
    assert PathStyle(None, Color(125, 14, 0), None, 5).hash == PathStyle(None, Color(125, 14, 0), None, 5).hash
    assert PathStyle(None, Color(125, 14, 0, 25), None, 5).hash == PathStyle(None, Color(125, 14, 0, 25), None, 5).hash
    assert PathStyle(None, Color(125, 14, 0), None, 5).hash == PathStyle(None, Color(125, 14, 0, 255), None, 5).hash
    assert (
        PathStyle(None, None, Solid(Color(124, 14, 0)), 5).hash
        == PathStyle(None, None, Solid(Color(124, 14, 0)), 5).hash
    )

    assert PathStyle(None, Color(125, 14, 0), None, 0).hash != PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
    assert (
        PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
        != PathStyle(Solid(Color(124, 14, 0)), None, None, 0).hash
    )
    assert (
        PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
        != PathStyle(Solid(Color(125, 15, 0)), None, None, 0).hash
    )
    assert (
        PathStyle(Solid(Color(125, 14, 0)), None, None, 0).hash
        != PathStyle(Solid(Color(125, 14, 1)), None, None, 0).hash
    )
    assert PathStyle(None, Color(125, 14, 0), None, 0).hash != PathStyle(None, Color(125, 14, 0), None, 1).hash
    assert PathStyle(None, Color(125, 14, 0, 25), None, 5).hash != PathStyle(None, Color(125, 14, 0, 24), None, 5).hash
    assert (
        PathStyle(None, None, Solid(Color(124, 15, 0)), 5).hash
        != PathStyle(None, None, Solid(Color(124, 14, 0)), 5).hash
    )


def test_is_line_style():
    assert PathStyle(None, Color(125, 14, 0), None, 5).is_line_style
    assert PathStyle(None, None, Solid(Color(125, 14, 0)), 5).is_line_style
    assert not PathStyle(Solid(Color(125, 14, 0)), None, None, 0).is_line_style


def test_is_empty_style():
    assert not PathStyle(None, Color(125, 14, 0), None, 5).is_empty
    assert not PathStyle(Solid(Color(125, 14, 0)), None, None, 0).is_empty
    assert PathStyle(None, Color(125, 14, 0), None, 0).is_empty
