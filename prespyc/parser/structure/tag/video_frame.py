"""VideoFrame tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class VideoFrameTag:
    """One encoded frame of a video stream."""

    TYPE: ClassVar[int] = 61

    stream_id: int
    frame_num: int
    video_data: bytes

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a VideoFrame tag, whose data ends at the `end` byte offset."""
        return cls(
            stream_id=reader.read_ui16(),
            frame_num=reader.read_ui16(),
            video_data=reader.read_bytes_to(end),
        )
