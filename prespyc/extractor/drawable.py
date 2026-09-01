"""Protocols for SWF characters that can be drawn."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle


@runtime_checkable
class Drawable(Protocol):
    """A SWF character that can be drawn: a shape, a morph shape, a sprite, an image, a timeline."""

    @property
    def bounds(self) -> Rectangle:
        """Size and offset of the character, in twips."""
        ...

    def frames_count(self, recursive: bool = False) -> int:
        """
        Number of frames in the character, at least 1.

        With `recursive`, count the frames of all children too.
        """
        ...

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        """
        Draw the character on `drawer` and return it.

        A `frame` past the last one draws the last frame.
        """
        ...

    def transform_colors(self, color_transform: ColorTransform) -> Drawable:
        """
        Transform the colors of the character, recursively, and return a new instance.

        The current instance is never modified.
        """
        ...

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> Drawable:
        """
        Apply `modifier` to the character and its children, and return a new instance.

        `max_depth` is the depth to recurse to: -1 for no limit, 0 for the character alone. When
        children change, the character is updated to match (bounds and so on). When nothing changes,
        the current instance may be returned.
        """
        ...


@runtime_checkable
class RatioDrawable(Drawable, Protocol):
    """A drawable whose shape depends on a ratio, i.e. a morph shape."""

    MAX_RATIO: ClassVar[int] = 65535

    def with_ratio(self, ratio: int) -> Drawable:
        """The drawable at `ratio`, between 0 and `MAX_RATIO`."""
        ...
