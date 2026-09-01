"""Port of `tests/Extractor/Shape/FillType/LinearGradientTest.php`."""

from __future__ import annotations

from dataclasses import astuple

import pytest

from prespyc.extractor.shape.fill_type.gradient import LinearGradient
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient import Gradient
from prespyc.parser.structure.record.gradient_record import GradientRecord
from prespyc.parser.structure.record.matrix import Matrix


def test_interpolate():
    start = LinearGradient(
        Matrix(1.0, 0.0, 0.0, 1.0, 0, 0),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(200, 100, 0, 0)),
                GradientRecord(255, Color(10, 128, 255, 255)),
            ],
        ),
    )
    end = LinearGradient(
        Matrix(0.5, 0.0, 0.0, 0.5, 10, 20),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(0, 50, 200, 255)),
                GradientRecord(255, Color(255, 255, 255, 0)),
            ],
        ),
    )

    assert start.interpolate(end, 0) == start
    assert start.interpolate(end, 65535) == end

    expected = LinearGradient(
        Matrix(0.75, 0.0, 0.0, 0.75, 5, 10),
        Gradient(
            Gradient.SPREAD_MODE_PAD,
            Gradient.INTERPOLATION_MODE_LINEAR,
            [
                GradientRecord(0, Color(99, 74, 100, 127)),
                GradientRecord(255, Color(132, 191, 255, 127)),
            ],
        ),
    )
    actual = start.interpolate(end, 32768)

    # The matrix factors are interpolated as floats, so they only match within a delta.
    assert astuple(actual.matrix) == pytest.approx(astuple(expected.matrix), abs=0.0001)
    assert actual.gradient == expected.gradient
