"""PlaceObject2 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.clip_actions import ClipActions
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class PlaceObject2Tag:
    """Adds a character to the display list, or modifies the one already at that depth."""

    TYPE: ClassVar[int] = 26

    move: bool
    """Modify the character already at `depth` instead of adding a new one."""

    depth: int
    character_id: int | None
    matrix: Matrix | None
    color_transform: ColorTransform | None

    ratio: int | None
    """Morph ratio, between 0 and 65535."""

    name: bytes | None
    clip_depth: int | None
    clip_actions: ClipActions | None

    @classmethod
    def read(cls, reader: Reader, swf_version: int) -> Self:
        """Read a PlaceObject2 tag. `swf_version` is the SWF version of the file being read."""
        flags = reader.read_ui8()
        has_clip_actions = (flags & 0b10000000) != 0
        has_clip_depth = (flags & 0b01000000) != 0
        has_name = (flags & 0b00100000) != 0
        has_ratio = (flags & 0b00010000) != 0
        has_color_transform = (flags & 0b00001000) != 0
        has_matrix = (flags & 0b00000100) != 0
        has_character = (flags & 0b00000010) != 0
        move = (flags & 0b00000001) != 0

        return cls(
            move=move,
            depth=reader.read_ui16(),
            character_id=reader.read_ui16() if has_character else None,
            matrix=Matrix.read(reader) if has_matrix else None,
            color_transform=ColorTransform.read(reader, with_alpha=True) if has_color_transform else None,
            ratio=reader.read_ui16() if has_ratio else None,
            name=reader.read_null_terminated_string() if has_name else None,
            clip_depth=reader.read_ui16() if has_clip_depth else None,
            clip_actions=ClipActions.read(reader, swf_version) if has_clip_actions else None,
        )
