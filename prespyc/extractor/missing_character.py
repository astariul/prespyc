"""Placeholder for a character that does not exist."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.extractor.drawer.drawer import Drawer
    from prespyc.extractor.modifier.character_modifier import CharacterModifier
    from prespyc.parser.structure.record.color_transform import ColorTransform

_EMPTY_BOUNDS = Rectangle(0, 0, 0, 0)


@dataclass(frozen=True, slots=True)
class MissingCharacter:
    """A character id that the file does not define. Drawing it is a no-op."""

    id: int

    @property
    def bounds(self) -> Rectangle:
        return _EMPTY_BOUNDS

    def frames_count(self, recursive: bool = False) -> int:
        return 1

    def draw(self, drawer: Drawer, frame: int = 0) -> Drawer:
        return drawer

    def transform_colors(self, color_transform: ColorTransform) -> MissingCharacter:
        return self

    def modify(self, modifier: CharacterModifier, max_depth: int = -1) -> MissingCharacter:
        return self
