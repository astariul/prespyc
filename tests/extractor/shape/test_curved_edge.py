"""Port of `tests/Extractor/Shape/CurvedEdgeTest.php`."""

from __future__ import annotations

from unittest.mock import Mock

from prespyc.extractor.shape.edge import CurvedEdge, StraightEdge


def test_curved_edge():
    edge = CurvedEdge(10, 5, 20, 15, 30, 25)

    assert edge.from_x == 10
    assert edge.from_y == 5
    assert edge.control_x == 20
    assert edge.control_y == 15
    assert edge.to_x == 30
    assert edge.to_y == 25

    drawer = Mock()
    edge.draw(drawer)
    drawer.curve.assert_called_once_with(20, 15, 30, 25)

    assert edge.reverse() == CurvedEdge(30, 25, 20, 15, 10, 5)


def test_interpolate_with_curved_edge():
    edge = CurvedEdge(10, 5, 20, 15, 30, 25)
    other = CurvedEdge(40, -25, 50, -15, 60, -5)

    assert edge.interpolate(other, 0) == CurvedEdge(10, 5, 20, 15, 30, 25)
    assert edge.interpolate(other, 32768) == CurvedEdge(25, -10, 35, 0, 45, 9)
    assert edge.interpolate(other, 65535) == CurvedEdge(40, -25, 50, -15, 60, -5)
    assert edge.interpolate(other, 15236) == CurvedEdge(16, -1, 26, 8, 36, 18)


def test_interpolate_with_straight_edge():
    edge = CurvedEdge(10, 5, 20, 15, 30, 25)
    other = StraightEdge(40, -25, 60, -5)

    assert edge.interpolate(other, 0) == CurvedEdge(10, 5, 20, 15, 30, 25)
    assert edge.interpolate(other, 32768) == CurvedEdge(25, -10, 35, 0, 45, 9)
    assert edge.interpolate(other, 65535) == CurvedEdge(40, -25, 50, -15, 60, -5)
    assert edge.interpolate(other, 15236) == CurvedEdge(16, -1, 26, 8, 36, 18)
