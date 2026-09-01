"""PlaceObject tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class PlaceObjectTag:
    """Adds a character to the display list at a given depth."""

    TYPE: ClassVar[int] = 4

    character_id: int
    depth: int
    matrix: Matrix
    color_transform: ColorTransform | None

    @classmethod
    def read(cls, reader: Reader, end: int) -> Self:
        """Read a PlaceObject tag, whose data ends at the `end` byte offset."""
        return cls(
            character_id=reader.read_ui16(),
            depth=reader.read_ui16(),
            matrix=Matrix.read(reader),
            color_transform=ColorTransform.read(reader, False) if reader.offset < end else None,
        )
