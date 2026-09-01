"""Building the paths of a shape."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.shape.path import Path

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.extractor.shape.edge import Edge
    from prespyc.extractor.shape.path_style import PathStyle


class PathsBuilder:
    """
    Builds the paths of a shape: associates styles to paths, and merges them when possible.
    """

    __slots__ = ("_active_styles", "_closed_paths", "_finalized_paths", "_open_paths")

    def __init__(self) -> None:
        self._open_paths: dict[str, Path] = {}
        """Paths that are in the process of being built, by style hash."""

        self._closed_paths: list[Path] = []
        """
        Paths that have been built, so no more edges can be added.

        Note: those paths are not yet finalized (i.e. not yet fixed nor ordered).
        """

        self._finalized_paths: list[Path] = []
        """
        Paths ready to be exported: already fixed and ordered (i.e. polygons are properly closed,
        and line paths are placed after fill paths).
        """

        self._active_styles: Sequence[PathStyle | None] = ()

    def set_active_styles(self, *styles: PathStyle | None) -> None:
        """
        Set the styles used to draw the following paths. A `None` style is ignored.
        """
        self._active_styles = styles

    def merge(self, *edges: Edge) -> None:
        """Merge new edges into all open paths with the active styles."""
        for style in self._active_styles:
            if style is None:
                continue

            to_push = self._reverse_edges(edges) if style.reverse else edges
            last_path = self._open_paths.get(style.hash)

            if last_path is None:
                self._open_paths[style.hash] = Path(list(to_push), style)
            else:
                self._open_paths[style.hash] = last_path.push(*to_push)

    def close(self) -> None:
        """
        Close all active paths.

        Call this when the drawing context changes (e.g. new styles). `export()` calls it already.
        """
        for path in self._open_paths.values():
            self._closed_paths.append(path)

        self._open_paths = {}

    def finalize(self) -> None:
        """Finalize the drawing of all active paths, so a new drawing context can start."""
        self._finalized_paths = self.export()
        self._closed_paths = []

    def export(self) -> list[Path]:
        """Export all built paths."""
        self.close()

        fill_paths: list[Path] = []
        line_paths: list[Path] = []

        for path in self._closed_paths:
            fixed_path = path.fix()

            if fixed_path.style.is_line_style:
                line_paths.append(fixed_path)
            else:
                fill_paths.append(fixed_path)

        # Line paths should be drawn after fill paths
        return [*self._finalized_paths, *fill_paths, *line_paths]

    @staticmethod
    def _reverse_edges(edges: Sequence[Edge]) -> list[Edge]:
        """Reverse each edge, and reverse their order."""
        reversed_edges: list[Edge] = []

        for edge in reversed(edges):
            reversed_edges.append(edge.reverse())

        return reversed_edges
