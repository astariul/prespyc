"""Encoded image data with its type."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.parser.structure.record.image_data_type import ImageDataType


@dataclass(frozen=True, slots=True)
class ImageData:
    """An encoded image blob and the format it is in."""

    type: ImageDataType
    data: bytes

    @property
    def base64_url(self) -> str:
        """
        The data as a `data:<mime>;base64,...` URL, for an `href` attribute or an image source.
        """
        return f"data:{self.type.mime_type};base64,{base64.b64encode(self.data).decode('ascii')}"
