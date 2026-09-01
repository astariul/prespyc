"""Edges of a shape path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prespyc.extractor.shape.path_drawer import PathDrawer


@runtime_checkable
class Edge(Protocol):
    """A single edge of a shape. Coordinates are in twips (1/20th of a pixel)."""

    from_x: int
    from_y: int
    to_x: int
    to_y: int

    def reverse(self) -> Edge:
        """The same edge, walked the other way."""
        ...

    def draw(self, drawer: PathDrawer) -> None:
        """Draw the edge, continuing from the drawer's cursor."""
        ...

    def interpolate(self, to: Edge, ratio: int) -> Edge:
        """The edge between this one and `to`, at `ratio` (0 = this edge, 65535 = `to`)."""
        ...


@dataclass(frozen=True, slots=True)
class StraightEdge:
    """A line."""

    from_x: int
    from_y: int
    to_x: int
    to_y: int

    def reverse(self) -> StraightEdge:
        return StraightEdge(self.to_x, self.to_y, self.from_x, self.from_y)

    def draw(self, drawer: PathDrawer) -> None:
        drawer.line(self.to_x, self.to_y)

    def to_curved_edge(self) -> CurvedEdge:
        """The equivalent curve, with the control point in the middle."""
        return CurvedEdge(
            self.from_x,
            self.from_y,
            int((self.from_x + self.to_x) / 2),
            int((self.from_y + self.to_y) / 2),
            self.to_x,
            self.to_y,
        )

    def interpolate(self, to: Edge, ratio: int) -> Edge:
        from prespyc.extractor.morph_shape.interpolate import interpolate_int

        if isinstance(to, StraightEdge):
            return StraightEdge(
                interpolate_int(self.from_x, to.from_x, ratio),
                interpolate_int(self.from_y, to.from_y, ratio),
                interpolate_int(self.to_x, to.to_x, ratio),
                interpolate_int(self.to_y, to.to_y, ratio),
            )

        return self.to_curved_edge().interpolate(to, ratio)


@dataclass(frozen=True, slots=True)
class CurvedEdge:
    """A quadratic curve."""

    from_x: int
    from_y: int
    control_x: int
    control_y: int
    to_x: int
    to_y: int

    def reverse(self) -> CurvedEdge:
        return CurvedEdge(self.to_x, self.to_y, self.control_x, self.control_y, self.from_x, self.from_y)

    def draw(self, drawer: PathDrawer) -> None:
        drawer.curve(self.control_x, self.control_y, self.to_x, self.to_y)

    def interpolate(self, to: Edge, ratio: int) -> CurvedEdge:
        from prespyc.extractor.morph_shape.interpolate import interpolate_int

        if isinstance(to, StraightEdge):
            to = to.to_curved_edge()

        assert isinstance(to, CurvedEdge)

        return CurvedEdge(
            interpolate_int(self.from_x, to.from_x, ratio),
            interpolate_int(self.from_y, to.from_y, ratio),
            interpolate_int(self.control_x, to.control_x, ratio),
            interpolate_int(self.control_y, to.control_y, ratio),
            interpolate_int(self.to_x, to.to_x, ratio),
            interpolate_int(self.to_y, to.to_y, ratio),
        )
