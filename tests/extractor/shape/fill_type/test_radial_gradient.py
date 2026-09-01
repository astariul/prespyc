"""Port of `tests/Extractor/Shape/FillType/RadialGradientTest.php`."""

from __future__ import annotations

from dataclasses import astuple

import pytest

from prespyc.extractor.shape.fill_type.gradient import RadialGradient
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.gradient_record import GradientRecord
from prespyc.parser.structure.record.matrix import Matrix


def test_interpolate():
    start = RadialGradient(
        Matrix(1.0, 0.0, 0.0, 1.0, 0, 0),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(200, 100, 0, 0)),
                GradientRecord(255, Color(10, 128, 255, 255)),
            ],
            12.3,
        ),
    )
    end = RadialGradient(
        Matrix(0.5, 0.0, 0.0, 0.5, 10, 20),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(0, 50, 200, 255)),
                GradientRecord(255, Color(255, 255, 255, 0)),
            ],
            3.65,
        ),
    )

    assert start.interpolate(end, 0) == start
    assert start.interpolate(end, 65535) == end

    expected = RadialGradient(
        Matrix(0.75, 0.0, 0.0, 0.75, 5, 10),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(99, 74, 100, 127)),
                GradientRecord(255, Color(132, 191, 255, 127)),
            ],
            7.975,
        ),
    )
    actual = start.interpolate(end, 32768)

    # The matrix factors and the focal point are interpolated as floats: only match within a delta.
    assert astuple(actual.matrix) == pytest.approx(astuple(expected.matrix), abs=0.0001)
    assert actual.gradient.spread_mode == expected.gradient.spread_mode
    assert actual.gradient.interpolation_mode == expected.gradient.interpolation_mode
    assert actual.gradient.records == expected.gradient.records
    assert actual.gradient.focal_point == pytest.approx(expected.gradient.focal_point, abs=0.0001)
