"""Port of ArakneSwf's `tests/Parser/Structure/Record/MatrixTest.php`."""

from __future__ import annotations

from prespyc.parser.structure.record.matrix import Matrix
from tests.support import fixture, fixture_reader


def test_read_only_translate():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 195)

    matrix = Matrix.read(reader)

    assert matrix.scale_x == 1.0
    assert matrix.scale_y == 1.0
    assert matrix.rotate_skew0 == 0.0
    assert matrix.rotate_skew1 == 0.0
    assert matrix.translate_x == 40
    assert matrix.translate_y == 40


def test_read_empty():
    reader = fixture_reader(fixture("139.swf"), 1895)

    matrix = Matrix.read(reader)

    assert matrix.scale_x == 1.0
    assert matrix.scale_y == 1.0
    assert matrix.rotate_skew0 == 0.0
    assert matrix.rotate_skew1 == 0.0
    assert matrix.translate_x == 0
    assert matrix.translate_y == 0


def test_read_all_parameters():
    reader = fixture_reader(fixture("1317.swf"), 2075)

    matrix = Matrix.read(reader)

    assert matrix.scale_x == -0.477874755859375
    assert matrix.scale_y == 0.477874755859375
    assert matrix.rotate_skew0 == -0.8749542236328125
    assert matrix.rotate_skew1 == -0.8749542236328125
    assert matrix.translate_x == -102
    assert matrix.translate_y == -1363


def test_compose_applies_the_right_matrix_first():
    parent = Matrix(scale_x=2.0, scale_y=2.0, translate_x=10, translate_y=20)
    child = Matrix(translate_x=5, translate_y=-5)

    assert parent @ child == Matrix(scale_x=2.0, scale_y=2.0, translate_x=20, translate_y=10)
    assert child @ parent == Matrix(scale_x=2.0, scale_y=2.0, translate_x=15, translate_y=15)


def test_compose_rotations():
    import math

    def rotation(degrees: float) -> Matrix:
        angle = math.radians(degrees)
        return Matrix(math.cos(angle), math.cos(angle), math.sin(angle), -math.sin(angle))

    composed = rotation(30) @ rotation(60)

    assert math.isclose(composed.scale_x, 0.0, abs_tol=1e-12)
    assert math.isclose(composed.rotate_skew0, 1.0)
    assert math.isclose(composed.rotate_skew1, -1.0)
    assert math.isclose(composed.scale_y, 0.0, abs_tol=1e-12)


def test_compose_transforms_a_point_like_both_matrices():
    parent = Matrix(scale_x=0.5, scale_y=1.5, rotate_skew0=0.25, rotate_skew1=-0.75, translate_x=100, translate_y=-40)
    child = Matrix(scale_x=-1.0, scale_y=2.0, rotate_skew0=0.5, translate_x=30, translate_y=12)

    x, y = child.transform_x(64, -32), child.transform_y(64, -32)

    assert (parent @ child).transform_x(64, -32) == parent.transform_x(x, y)
    assert (parent @ child).transform_y(64, -32) == parent.transform_y(x, y)
