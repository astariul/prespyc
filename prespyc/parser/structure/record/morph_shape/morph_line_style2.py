"""Morph line style record, version 2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.morph_shape.morph_fill_style import MorphFillStyle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class MorphLineStyle2:
    """The line style of a morph shape, with caps, joins and an optional fill style."""

    CAP_ROUND: ClassVar[int] = 0
    CAP_NONE: ClassVar[int] = 1
    CAP_SQUARE: ClassVar[int] = 2
    JOIN_ROUND: ClassVar[int] = 0
    JOIN_BEVEL: ClassVar[int] = 1
    JOIN_MITER: ClassVar[int] = 2

    start_width: int
    end_width: int
    start_cap_style: int
    join_style: int
    no_h_scale: bool
    no_v_scale: bool
    pixel_hinting: bool
    no_close: bool
    end_cap_style: int

    miter_limit_factor: int | None
    """
    Only used if `join_style` is `JOIN_MITER`. The value is a fixed 8.8 number.

    An int, to stay compatible with `LineStyle.miter_limit_factor`.
    """

    start_color: Color | None
    end_color: Color | None
    fill_style: MorphFillStyle | None

    @classmethod
    def read_collection(cls, reader: Reader) -> list[Self]:
        """
        Read a MorphLineStyle2 collection.

        The collection size is determined by the first byte read (or 3 if extended).
        """
        count = reader.read_ui8()
        styles: list[Self] = []

        if count == 0xFF:
            count = reader.read_ui16()

        for _ in range(count):
            start_width = reader.read_ui16()
            end_width = reader.read_ui16()

            flags = reader.read_ui8()
            start_cap_style = (flags >> 6) & 3  # 2 bits
            join_style = (flags >> 4) & 3  # 2 bits
            has_fill = (flags & 0b00001000) != 0
            no_h_scale = (flags & 0b00000100) != 0
            no_v_scale = (flags & 0b00000010) != 0
            pixel_hinting = (flags & 0b00000001) != 0

            flags = reader.read_ui8()
            # 5 bits reserved (should be 0)
            no_close = (flags & 0b00000100) != 0
            end_cap_style = flags & 0b00000011

            styles.append(
                cls(
                    start_width=start_width,
                    end_width=end_width,
                    start_cap_style=start_cap_style,
                    join_style=join_style,
                    no_h_scale=no_h_scale,
                    no_v_scale=no_v_scale,
                    pixel_hinting=pixel_hinting,
                    no_close=no_close,
                    end_cap_style=end_cap_style,
                    miter_limit_factor=reader.read_ui16() if join_style == cls.JOIN_MITER else None,
                    start_color=Color.read_rgba(reader) if not has_fill else None,
                    end_color=Color.read_rgba(reader) if not has_fill else None,
                    fill_style=MorphFillStyle.read(reader) if has_fill else None,
                )
            )

        return styles
