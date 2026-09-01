"""Computing the output size of a rendered drawable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class ImageResizer(Protocol):
    """Computes the size of a resized image."""

    def scale(self, width: float, height: float) -> tuple[float, float]:
        """
        New `(width, height)` in pixels, from the original size in pixels.

        Sizes are floats because SWF works in twips (1/20th of a pixel).
        """
        ...


@dataclass(frozen=True, slots=True)
class FitSizeResizer:
    """
    Fits the image inside `width` x `height`, keeping the aspect ratio.

    The larger dimension is resized to the given size and the other follows proportionally.
    """

    width: int
    height: int

    def scale(self, width: float, height: float) -> tuple[float, float]:
        if width == 0.0 and height == 0.0:
            return float(self.width), float(self.height)

        if width == 0.0:
            return 0.0, float(self.height)

        if height == 0.0:
            return float(self.width), 0.0

        factor = max(width / self.width, height / self.height)

        return width / factor, height / factor


@dataclass(frozen=True, slots=True)
class ScaleResizer:
    """Resizes the image by a fixed factor, which must be greater than 0."""

    scale_factor: float

    def __post_init__(self) -> None:
        assert self.scale_factor > 0.0

    def scale(self, width: float, height: float) -> tuple[float, float]:
        return width * self.scale_factor, height * self.scale_factor
