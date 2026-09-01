"""Protocol for drawing a single path."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class PathDrawer(Protocol):
    """
    Draws one path. Stateful: use one instance per path.

    Coordinates are in twips (1/20th of a pixel).
    """

    def move(self, x: int, y: int) -> None:
        """Move the cursor."""
        ...

    def line(self, to_x: int, to_y: int) -> None:
        """Draw a line from the cursor and move it to the end point."""
        ...

    def curve(self, control_x: int, control_y: int, to_x: int, to_y: int) -> None:
        """Draw a quadratic curve from the cursor and move it to the end point."""
        ...

    def draw(self) -> None:
        """Finalize and draw the path."""
        ...
