"""Placing a `FrameObject` the way a PlaceObject tag does."""

from __future__ import annotations

from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.swf_file import SwfFile
from tests.support import fixture


def _extractor():
    return SwfFile(fixture("extractor", "1047", "1047.swf")).extractor


def test_place_offsets_the_matrix_by_the_object_bounds() -> None:
    head = _extractor()[13]  # bounds start at (-50, 49)
    tag_matrix = Matrix(scale_x=2.0, scale_y=2.0, translate_x=100, translate_y=-40)

    placed = FrameObject.place(3, head, tag_matrix)

    assert placed.depth == 3
    assert placed.matrix == Matrix(scale_x=2.0, scale_y=2.0, translate_x=0, translate_y=58)
    assert placed.bounds == head.bounds.transform(tag_matrix)
    assert placed.tag_matrix == tag_matrix


def test_tag_matrix_of_a_parsed_placement() -> None:
    # Sprite 23 (bounds from (-108, -17)) is placed at depth 19 by an untransformed tag.
    placed = _extractor()[65].timeline.frames[0].objects[19]

    assert placed.matrix == Matrix(translate_x=-94, translate_y=-365)
    assert placed.tag_matrix == Matrix(translate_x=14, translate_y=-348)


def test_with_placement_swaps_the_object_and_keeps_the_rest() -> None:
    extractor = _extractor()
    placed = extractor[65].timeline.frames[0].objects[1]
    other = extractor[13]

    swapped = placed.with_placement(other)

    assert swapped.object is other
    assert swapped.matrix == placed.tag_matrix.translate(other.bounds.xmin, other.bounds.ymin)
    assert swapped.bounds == other.bounds.transform(placed.tag_matrix)
    assert swapped.color_transform == placed.color_transform
    assert (swapped.depth, swapped.name, swapped.blend_mode) == (placed.depth, placed.name, placed.blend_mode)


def test_with_placement_moves_the_object() -> None:
    placed = _extractor()[65].timeline.frames[0].objects[1]
    tag_matrix = Matrix(translate_x=200)

    moved = placed.with_placement(tag_matrix=tag_matrix)

    assert moved.object is placed.object
    assert moved.tag_matrix == tag_matrix
    assert moved.bounds == placed.object.bounds.transform(tag_matrix)
    assert moved.color_transform == placed.color_transform
