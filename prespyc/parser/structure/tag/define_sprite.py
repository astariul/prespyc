"""DefineSprite tag: a nested timeline, holding its own tag stream."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.errors import Errors, ParserError

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineSpriteTag:
    """A sprite character: a movie clip with its own display list and frames."""

    TYPE: ClassVar[int] = 39

    sprite_id: int
    frame_count: int
    tags: list[object]
    """Parsed tags of the sprite timeline."""

    @classmethod
    def read(cls, reader: Reader, swf_version: int, end: int) -> Self:
        """Read a DefineSprite tag, whose data ends at the `end` byte offset."""
        # Imported here because `raw_tag` imports every tag module.
        from prespyc.parser.structure.raw_tag import RawTag

        ignore_tag_error = (reader.errors & Errors.INVALID_TAG) == 0
        sprite_id = reader.read_ui16()
        frame_count = reader.read_ui16()

        # Collect and parse tags
        tags: list[object] = []

        for raw_tag in RawTag.read_all(reader, end, False):
            try:
                tags.append(raw_tag.parse(reader, swf_version))
            except ParserError:
                if not ignore_tag_error:
                    raise

        return cls(
            sprite_id=sprite_id,
            frame_count=frame_count,
            tags=tags,
        )
