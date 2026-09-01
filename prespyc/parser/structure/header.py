"""SWF file header."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prespyc.parser.structure.record.rectangle import Rectangle


@dataclass(frozen=True, slots=True)
class Header:
    """The fixed part of a SWF file, before the tags."""

    signature: str
    """`"FWS"` for an uncompressed file, `"CWS"` for a ZLib compressed one."""

    version: int
    """SWF version of the file."""

    file_length: int
    """Length of the file in bytes. For a compressed file, the *uncompressed* length."""

    frame_size: Rectangle
    """Display bounds of the frames, in twips."""

    frame_rate: float
    """Frames per second, as a 8.8 fixed point number."""

    frame_count: int
