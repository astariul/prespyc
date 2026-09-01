"""Protocol for the draw operations a drawable emits."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from prespyc.extractor.timeline.blend_mode import BlendMode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.image.image_character import ImageCharacter
    from prespyc.extractor.shape.path import Path
    from prespyc.extractor.shape.shape import Shape
    from prespyc.parser.structure.record.filter.filter import Filter
    from prespyc.parser.structure.record.matrix import Matrix
    from prespyc.parser.structure.record.rectangle import Rectangle


@runtime_checkable
class Drawer(Protocol):
    """
    Receives the draw operations of a `Drawable`.

    Implementations are stateful: one drawer per rendering.
    """

    def area(self, bounds: Rectangle) -> None:
        """Start a new drawing area."""
        ...

    def shape(self, shape: Shape) -> None:
        """Draw a shape."""
        ...

    def image(self, image: ImageCharacter) -> None:
        """Draw a raster image."""
        ...

    def include(
        self,
        obj: Drawable,
        matrix: Matrix,
        frame: int = 0,
        filters: Sequence[Filter] = (),
        blend_mode: BlendMode = BlendMode.NORMAL,
        name: str | None = None,
    ) -> None:
        """Include a sprite or shape in the current drawing."""
        ...

    def start_clip(self, obj: Drawable, matrix: Matrix, frame: int) -> str:
        """
        Use `obj` as a clipping mask for every following operation, until `end_clip()`.

        Returns the id of the clip, to pass to `end_clip()`.
        """
        ...

    def end_clip(self, clip_id: str) -> None:
        """Stop the clipping mask `clip_id`, as returned by `start_clip()`."""
        ...

    def path(self, path: Path) -> None:
        """Draw a path."""
        ...

    def render(self):
        """Render the drawing. The return type depends on the implementation."""
        ...
