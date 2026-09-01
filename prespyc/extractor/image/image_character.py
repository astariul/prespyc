"""Protocol for raster image characters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from prespyc.extractor.drawable import Drawable

if TYPE_CHECKING:
    from prespyc.extractor.image.image_data import ImageData
    from prespyc.parser.structure.record.color_transform import ColorTransform
    from prespyc.parser.structure.record.rectangle import Rectangle


@runtime_checkable
class ImageCharacter(Drawable, Protocol):
    """A raster image defined in a SWF file."""

    character_id: int
    """Character id of the image in the SWF file."""

    @property
    def bounds(self) -> Rectangle:
        """
        Size of the image in twips. Raster images have no offset, so the bounds are always
        `(0, 0, width, height)`.
        """
        ...

    def transform_colors(self, color_transform: ColorTransform) -> ImageCharacter:
        """
        Transform the colors of the image and return a new instance.

        The returned type differs from the original: it stores the transformed pixels directly.
        """
        ...

    def to_base64_data(self) -> str:
        """
        The image as a data URL, starting with `data:image/png;base64,` or
        `data:image/jpeg;base64,` depending on the best format for the data.
        """
        ...

    def to_png(self) -> bytes:
        """Render the image as PNG."""
        ...

    def to_jpeg(self, quality: int = -1) -> bytes:
        """
        Render the image as JPEG, losing the alpha channel if there is one.

        `quality` goes from 0 (worst) to 100 (best); -1 uses the default. Ignored when the image is
        already a JPEG.
        """
        ...

    def to_best_format(self) -> ImageData:
        """Render the image in the best format for its data."""
        ...
