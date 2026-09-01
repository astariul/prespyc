"""Protocol for the fill of a path."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color_transform import ColorTransform


@runtime_checkable
class FillType(Protocol):
    """How a path is filled: a solid color, a gradient or a bitmap."""

    @property
    def hash(self) -> str:
        """
        Content hash, used as the grouping key when building paths and as the SVG element id.

        It ends up in the golden SVG output, so it must match PHP byte for byte.
        """
        ...

    def transform_colors(self, color_transform: ColorTransform) -> FillType: ...
