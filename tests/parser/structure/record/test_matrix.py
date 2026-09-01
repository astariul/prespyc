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
