"""
Interpolation between the start and end state of a morph shape.

PHP keeps these as static methods on `MorphShape`, but the shape edges call them too, which would be
an import cycle in Python. They live here instead; `MorphShape` re-exports nothing, it just uses them.
"""

from __future__ import annotations

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.gradient_record import GradientRecord
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.parser.structure.record.rectangle import Rectangle

MAX_RATIO = 65535
"""Ratio of the end state. 0 is the start state."""


def interpolate_int(start: int, end: int, ratio: int) -> int:
    return int((start * (MAX_RATIO - ratio) + end * ratio) / MAX_RATIO)


def interpolate_float(start: float, end: float, ratio: int) -> float:
    return (start * (MAX_RATIO - ratio) + end * ratio) / MAX_RATIO


def interpolate_rectangle(start: Rectangle, end: Rectangle, ratio: int) -> Rectangle:
    return Rectangle(
        interpolate_int(start.xmin, end.xmin, ratio),
        interpolate_int(start.xmax, end.xmax, ratio),
        interpolate_int(start.ymin, end.ymin, ratio),
        interpolate_int(start.ymax, end.ymax, ratio),
    )


def interpolate_color(start: Color, end: Color, ratio: int) -> Color:
    start_alpha = start.alpha if start.alpha is not None else 255
    end_alpha = end.alpha if end.alpha is not None else 255

    return Color(
        interpolate_int(start.red, end.red, ratio),
        interpolate_int(start.green, end.green, ratio),
        interpolate_int(start.blue, end.blue, ratio),
        interpolate_int(start_alpha, end_alpha, ratio),
    )


def interpolate_matrix(start: Matrix, end: Matrix, ratio: int) -> Matrix:
    return Matrix(
        interpolate_float(start.scale_x, end.scale_x, ratio),
        interpolate_float(start.scale_y, end.scale_y, ratio),
        interpolate_float(start.rotate_skew0, end.rotate_skew0, ratio),
        interpolate_float(start.rotate_skew1, end.rotate_skew1, ratio),
        interpolate_int(start.translate_x, end.translate_x, ratio),
        interpolate_int(start.translate_y, end.translate_y, ratio),
    )


def interpolate_gradient(start: Gradient, end: Gradient, ratio: int) -> Gradient:
    assert len(start.records) == len(end.records)

    records = [
        GradientRecord(
            interpolate_int(start_record.ratio, end_record.ratio, ratio),
            interpolate_color(start_record.color, end_record.color, ratio),
        )
        for start_record, end_record in zip(start.records, end.records)
    ]

    focal_point = None

    if start.focal_point is not None and end.focal_point is not None:
        focal_point = interpolate_float(start.focal_point, end.focal_point, ratio)

    return Gradient(start.spread_mode, start.interpolation_mode, records, focal_point)
