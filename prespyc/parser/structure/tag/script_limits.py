"""ScriptLimits tag: the AVM recursion and timeout limits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class ScriptLimitsTag:
    """Overrides the player's default script recursion depth and timeout."""

    TYPE: ClassVar[int] = 65

    max_recursion_depth: int
    script_timeout_seconds: int

    @classmethod
    def read(cls, reader: Reader) -> Self:
        return cls(
            max_recursion_depth=reader.read_ui16(),
            script_timeout_seconds=reader.read_ui16(),
        )
