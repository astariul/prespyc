"""Common shape of the DefineBitsJPEG tags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prespyc.parser.structure.record.image_data_type import ImageDataType


@runtime_checkable
class DefineBitsJPEGTag(Protocol):
    """
    Shared surface of `DefineBitsJPEG2Tag`, `DefineBitsJPEG3Tag` and `DefineBitsJPEG4Tag`.

    The three tags satisfy it structurally and do not inherit it: on a dataclass, an inherited
    `property` would be picked up as a field default.
    """

    @property
    def type(self) -> ImageDataType:
        """The stored image data type."""
        ...

    @property
    def image_data(self) -> bytes:
        """
        Raw image data. Can be JPEG, PNG or GIF89a.

        Use `type` to get the image format.
        """
        ...

    @property
    def alpha_data(self) -> bytes | None:
        """
        Uncompressed alpha data as a byte array.

        Each byte is the opacity of the corresponding pixel in `image_data`. The length of this
        array must be equal to the decoded image width * height.

        Note: this field is only present if `image_data` is a JPEG image.
        """
        ...
