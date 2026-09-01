"""PlaceObject3 tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.clip_actions import ClipActions
from prespyc.parser.structure.record.color_transform import ColorTransform
from prespyc.parser.structure.record.filter.filter import Filter
from prespyc.parser.structure.record.matrix import Matrix

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class PlaceObject3Tag:
    """`PlaceObject2` extended with filters, a blend mode, bitmap caching and a class name."""

    TYPE: ClassVar[int] = 70

    move: bool
    """See `PlaceObject2Tag.move`."""

    has_image: bool
    """Introduced in PlaceObject3."""

    depth: int
    """See `PlaceObjectTag.depth`."""

    class_name: bytes | None
    """Introduced in PlaceObject3."""

    character_id: int | None
    """See `PlaceObjectTag.character_id`."""

    matrix: Matrix | None
    """See `PlaceObjectTag.matrix`."""

    color_transform: ColorTransform | None
    """See `PlaceObjectTag.color_transform`."""

    ratio: int | None
    """See `PlaceObject2Tag.ratio`. Between 0 and 65535."""

    name: bytes | None
    """See `PlaceObject2Tag.name`."""

    clip_depth: int | None
    """See `PlaceObject2Tag.clip_depth`."""

    surface_filter_list: list[Filter] | None
    """Introduced in PlaceObject3."""

    blend_mode: int | None
    """Introduced in PlaceObject3."""

    bitmap_cache: int | None
    """Introduced in PlaceObject3."""

    clip_actions: ClipActions | None
    """See `PlaceObject2Tag.clip_actions`."""

    @classmethod
    def read(cls, reader: Reader, swf_version: int) -> Self:
        """Read a PlaceObject3 tag. `swf_version` is the SWF version of the file being read."""
        flags = reader.read_ui8()
        place_flag_has_clip_actions = (flags & 0b10000000) != 0
        place_flag_has_clip_depth = (flags & 0b01000000) != 0
        place_flag_has_name = (flags & 0b00100000) != 0
        place_flag_has_ratio = (flags & 0b00010000) != 0
        place_flag_has_color_transform = (flags & 0b00001000) != 0
        place_flag_has_matrix = (flags & 0b00000100) != 0
        place_flag_has_character = (flags & 0b00000010) != 0
        place_flag_move = (flags & 0b00000001) != 0

        flags = reader.read_ui8()
        # 3 bits reserved, must be 0
        place_flag_has_image = (flags & 0b00010000) != 0
        place_flag_has_class_name = (flags & 0b00001000) != 0
        place_flag_has_cache_as_bitmap = (flags & 0b00000100) != 0
        place_flag_has_blend_mode = (flags & 0b00000010) != 0
        place_flag_has_filter_list = (flags & 0b00000001) != 0

        return cls(
            move=place_flag_move,
            has_image=place_flag_has_image,
            depth=reader.read_ui16(),
            class_name=(
                reader.read_null_terminated_string()
                if place_flag_has_class_name or (place_flag_has_image and place_flag_has_character)
                else None
            ),
            character_id=reader.read_ui16() if place_flag_has_character else None,
            matrix=Matrix.read(reader) if place_flag_has_matrix else None,
            color_transform=ColorTransform.read(reader, True) if place_flag_has_color_transform else None,
            ratio=reader.read_ui16() if place_flag_has_ratio else None,
            name=reader.read_null_terminated_string() if place_flag_has_name else None,
            clip_depth=reader.read_ui16() if place_flag_has_clip_depth else None,
            surface_filter_list=Filter.read_collection(reader) if place_flag_has_filter_list else None,
            blend_mode=reader.read_ui8() if place_flag_has_blend_mode else None,
            bitmap_cache=reader.read_ui8() if place_flag_has_cache_as_bitmap else None,
            clip_actions=ClipActions.read(reader, swf_version) if place_flag_has_clip_actions else None,
        )
