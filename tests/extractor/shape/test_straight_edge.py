"""Port of `tests/Extractor/Shape/StraightEdgeTest.php`."""

from __future__ import annotations

from unittest.mock import Mock

from prespyc.extractor.shape.edge import CurvedEdge, StraightEdge


def test_straight_edge():
    edge = StraightEdge(10, 5, 20, 15)

    assert edge.from_x == 10
    assert edge.from_y == 5
    assert edge.to_x == 20
    assert edge.to_y == 15

    drawer = Mock()
    edge.draw(drawer)
    drawer.line.assert_called_once_with(20, 15)

    assert edge.reverse() == StraightEdge(20, 15, 10, 5)


def test_to_curved_edge():
    edge = StraightEdge(10, 5, 20, 15)
    curved_edge = edge.to_curved_edge()

    assert curved_edge.from_x == 10
    assert curved_edge.from_y == 5
    assert curved_edge.control_x == 15
    assert curved_edge.control_y == 10
    assert curved_edge.to_x == 20
    assert curved_edge.to_y == 15


def test_interpolate_with_straight_edge():
    edge = StraightEdge(10, 5, 20, 15)
    other = StraightEdge(30, -25, 40, 35)

    assert edge.interpolate(other, 0) == StraightEdge(10, 5, 20, 15)
    assert edge.interpolate(other, 32768) == StraightEdge(20, -10, 30, 25)
    assert edge.interpolate(other, 65535) == StraightEdge(30, -25, 40, 35)
    assert edge.interpolate(other, 15236) == StraightEdge(14, -1, 24, 19)


def test_interpolate_with_curved_edge():
    edge = StraightEdge(10, 5, 20, 15)
    other = CurvedEdge(30, -25, 35, 0, 40, 35)

    assert edge.interpolate(other, 0) == CurvedEdge(10, 5, 15, 10, 20, 15)
    assert edge.interpolate(other, 32768) == CurvedEdge(20, -10, 25, 4, 30, 25)
    assert edge.interpolate(other, 65535) == CurvedEdge(30, -25, 35, 0, 40, 35)
    assert edge.interpolate(other, 15236) == CurvedEdge(14, -1, 19, 7, 24, 19)
