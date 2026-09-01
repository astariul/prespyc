"""A polygon or line path."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.extractor.shape.edge import Edge
    from prespyc.extractor.shape.path_drawer import PathDrawer
    from prespyc.extractor.shape.path_style import PathStyle
    from prespyc.parser.structure.record.color_transform import ColorTransform


class Path:
    """
    A run of connected edges sharing one style.

    Mutable while the builder fills it in; treat it as immutable afterwards.
    """

    __slots__ = ("edges", "style")

    def __init__(self, edges: list[Edge], style: PathStyle) -> None:
        self.edges = edges
        self.style = style

    def push(self, *edges: Edge) -> Path:
        """
        Append edges. **Mutates** the path — only for use inside the builder.

        Returns the path itself.
        """
        self.edges.extend(edges)

        return self

    def fix(self) -> Path:
        """
        Reorder the edges so that they connect end to end, and return a new path.

        Flash tolerates disconnected edges, SVG does not. Walk the set of edges: take one, then
        repeatedly look for an edge starting (or, reversed, ending) where the current one ends. When
        nothing connects, start a new run with whatever is left. Edge *order* changes; the geometry
        does not.
        """
        remaining = {id(edge): edge for edge in self.edges}
        edges: list[Edge] = []

        while remaining:
            current_key = next(iter(remaining))
            current = remaining.pop(current_key)
            edges.append(current)

            while current is not None:
                found = False

                for other in remaining.values():
                    if current.to_x == other.from_x and current.to_y == other.from_y:
                        edges.append(other)
                        del remaining[id(other)]
                        current = other
                        found = True
                        break

                    if current.to_x == other.to_x and current.to_y == other.to_y:
                        reverse = other.reverse()
                        edges.append(reverse)
                        del remaining[id(other)]
                        current = reverse
                        found = True
                        break

                if not found:
                    break

        return Path(edges, self.style)

    def draw(self, drawer: PathDrawer) -> None:
        """Draw the path, moving the cursor whenever the next edge does not continue the last."""
        last_x = None
        last_y = None

        for edge in self.edges:
            if edge.from_x != last_x or edge.from_y != last_y:
                drawer.move(edge.from_x, edge.from_y)

            edge.draw(drawer)

            last_x = edge.to_x
            last_y = edge.to_y

        drawer.draw()

    def transform_colors(self, color_transform: ColorTransform) -> Path:
        return Path(self.edges, self.style.transform_colors(color_transform))
