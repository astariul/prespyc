"""DefineVideoStream tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineVideoStreamTag:
    """A video character: the frame count and codec of a video stream."""

    TYPE: ClassVar[int] = 60

    character_id: int
    num_frames: int
    width: int
    height: int
    deblocking: int
    smoothing: bool
    codec_id: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        character_id = reader.read_ui16()
        num_frames = reader.read_ui16()
        width = reader.read_ui16()
        height = reader.read_ui16()

        reader.skip_bits(4)  # Reserved
        deblocking = reader.read_ub(3)
        smoothing = reader.read_bool()

        codec_id = reader.read_ui8()

        return cls(
            character_id=character_id,
            num_frames=num_frames,
            width=width,
            height=height,
            deblocking=deblocking,
            smoothing=smoothing,
            codec_id=codec_id,
        )
