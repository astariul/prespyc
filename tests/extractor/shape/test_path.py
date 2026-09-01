"""Port of `tests/Extractor/Shape/PathTest.php`."""

from __future__ import annotations

import pytest

from prespyc.extractor.shape.edge import CurvedEdge, StraightEdge
from prespyc.extractor.shape.path import Path
from prespyc.extractor.shape.path_style import PathStyle


class StubDrawer:
    """A `PathDrawer` that records the commands it receives."""

    def __init__(self) -> None:
        self.commands: list[tuple] = []

    def move(self, x: int, y: int) -> None:
        self.commands.append(("move", x, y))

    def line(self, to_x: int, to_y: int) -> None:
        self.commands.append(("line", to_x, to_y))

    def curve(self, control_x: int, control_y: int, to_x: int, to_y: int) -> None:
        self.commands.append(("curve", control_x, control_y, to_x, to_y))

    def draw(self) -> None:
        pass


@pytest.fixture
def drawer() -> StubDrawer:
    return StubDrawer()


def test_draw(drawer: StubDrawer):
    path = Path(
        [
            StraightEdge(0, 0, 10, 15),
            StraightEdge(10, 15, 20, 20),
            CurvedEdge(20, 20, 30, 25, 40, 20),
        ],
        PathStyle(),
    )

    path.draw(drawer)

    assert drawer.commands == [
        ("move", 0, 0),
        ("line", 10, 15),
        ("line", 20, 20),
        ("curve", 30, 25, 40, 20),
    ]


def test_draw_not_connected(drawer: StubDrawer):
    path = Path(
        [
            StraightEdge(0, 0, 10, 15),
            StraightEdge(12, 22, 0, 42),
        ],
        PathStyle(),
    )

    path.draw(drawer)

    assert drawer.commands == [
        ("move", 0, 0),
        ("line", 10, 15),
        ("move", 12, 22),
        ("line", 0, 42),
    ]


def test_push(drawer: StubDrawer):
    path = Path(
        [
            StraightEdge(0, 0, 10, 15),
            StraightEdge(10, 15, 20, 20),
            CurvedEdge(20, 20, 30, 25, 40, 20),
        ],
        PathStyle(),
    )

    path.push(
        StraightEdge(40, 20, 50, 25),
        StraightEdge(50, 25, 60, 30),
    )

    path.draw(drawer)

    assert drawer.commands == [
        ("move", 0, 0),
        ("line", 10, 15),
        ("line", 20, 20),
        ("curve", 30, 25, 40, 20),
        ("line", 50, 25),
        ("line", 60, 30),
    ]


def test_fix_should_reorder_edges(drawer: StubDrawer):
    path = Path(
        [
            CurvedEdge(20, 20, 15, 15, 10, 10),
            StraightEdge(10, 15, 20, 20),
            StraightEdge(10, 10, 0, 0),
            StraightEdge(0, 0, 10, 15),
        ],
        PathStyle(),
    )

    fixed = path.fix()
    assert fixed is not path
    assert fixed != path

    fixed.draw(drawer)

    assert drawer.commands == [
        ("move", 20, 20),
        ("curve", 15, 15, 10, 10),
        ("line", 0, 0),
        ("line", 10, 15),
        ("line", 20, 20),
    ]


def test_fix_should_reverse_edge_for_reconnect(drawer: StubDrawer):
    path = Path(
        [
            StraightEdge(0, 0, 10, 15),
            StraightEdge(20, 20, 10, 15),
            CurvedEdge(10, 10, 15, 15, 20, 20),
            StraightEdge(10, 10, 0, 0),
        ],
        PathStyle(),
    )

    fixed = path.fix()
    assert fixed is not path
    assert fixed != path

    fixed.draw(drawer)

    assert drawer.commands == [
        ("move", 0, 0),
        ("line", 10, 15),
        ("line", 20, 20),
        ("curve", 15, 15, 10, 10),
        ("line", 0, 0),
    ]


def test_fix_with_disjunct_path(drawer: StubDrawer):
    path = Path(
        [
            StraightEdge(10, 15, 0, 0),
            StraightEdge(0, 0, 10, 10),
            StraightEdge(10, 10, 10, 15),
            StraightEdge(30, 25, 20, 20),
            StraightEdge(20, 20, 30, 30),
            StraightEdge(30, 30, 30, 25),
        ],
        PathStyle(),
    )

    fixed = path.fix()
    fixed.draw(drawer)

    assert drawer.commands == [
        ("move", 10, 15),
        ("line", 0, 0),
        ("line", 10, 10),
        ("line", 10, 15),
        ("move", 30, 25),
        ("line", 20, 20),
        ("line", 30, 30),
        ("line", 30, 25),
    ]
