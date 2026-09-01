"""Image data type of the JPEG tags."""

from __future__ import annotations

from enum import Enum, auto

_PNG_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
_GIF89A_HEADER = b"GIF89a"


class ImageDataType(Enum):
    """
    Type of the image data on JPEG tags.

    Despite the tag names, `DefineBitsJPEG2Tag`, `DefineBitsJPEG3Tag` and `DefineBitsJPEG4Tag` may
    embed a PNG or a GIF89a image instead of a JPEG one.
    """

    JPEG = auto()
    PNG = auto()
    GIF89A = auto()

    @property
    def mime_type(self) -> str:
        """The MIME type of the image data."""
        return _MIME_TYPES[self]

    @property
    def extension(self) -> str:
        """The file extension of the image data."""
        return _EXTENSIONS[self]

    @classmethod
    def resolve(cls, image_data: bytes) -> ImageDataType:
        """Resolve the image data type from the image data header."""
        if image_data.startswith(_PNG_HEADER):
            return cls.PNG

        if image_data.startswith(_GIF89A_HEADER):
            return cls.GIF89A

        return cls.JPEG


_MIME_TYPES = {
    ImageDataType.JPEG: "image/jpeg",
    ImageDataType.PNG: "image/png",
    ImageDataType.GIF89A: "image/gif",
}

_EXTENSIONS = {
    ImageDataType.JPEG: "jpg",
    ImageDataType.PNG: "png",
    ImageDataType.GIF89A: "gif",
}
