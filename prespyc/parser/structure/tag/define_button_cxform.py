"""DefineButtonCxform tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color_transform import ColorTransform

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineButtonCxformTag:
    """The color transform applied to a button character."""

    TYPE: ClassVar[int] = 23

    button_id: int
    color_transform: ColorTransform

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            button_id=reader.read_ui16(),
            color_transform=ColorTransform.read(reader, with_alpha=False),
        )
