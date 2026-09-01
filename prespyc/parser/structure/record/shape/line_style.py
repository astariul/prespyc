"""Line style record."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.shape.fill_style import FillStyle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class LineStyle:
    """How the outline of a shape is stroked. Everything but the width is only set from version 4."""

    width: int
    """Stroke width, in twips. Never negative."""

    color: Color | None = None
    start_cap_style: int | None = None
    join_style: int | None = None
    has_fill_flag: bool | None = None
    no_h_scale_flag: bool | None = None
    no_v_scale_flag: bool | None = None
    pixel_hinting_flag: bool | None = None
    no_close: bool | None = None
    end_cap_style: int | None = None
    miter_limit_factor: int | None = None
    fill_type: FillStyle | None = None

    @classmethod
    def read_collection(cls, reader: Reader, version: int) -> list[Self]:
        """
        Read a collection of line styles from the reader.
        The count of elements is determined by the first byte (or 3 bytes for extended).

        `version` is the version of the shape tag, 1 to 4.
        """
        line_style_array = []
        line_style_count = reader.read_ui8()

        if line_style_count == 0xFF:
            line_style_count = reader.read_ui16()

        if version < 4:
            for _ in range(line_style_count):
                line_style_array.append(
                    cls(
                        width=reader.read_ui16(),
                        color=Color.read_rgb(reader) if version < 3 else Color.read_rgba(reader),
                    )
                )

            return line_style_array

        for _ in range(line_style_count):
            width = reader.read_ui16()

            flags = reader.read_ui8()
            start_cap_style = (flags >> 6) & 0b11  # 2bits
            join_style = (flags >> 4) & 0b11  # 4bits
            has_fill_flag = (flags & 0b1000) != 0  # 5bits
            no_h_scale_flag = (flags & 0b100) != 0  # 6bits
            no_v_scale_flag = (flags & 0b10) != 0  # 7 bits
            pixel_hinting_flag = (flags & 0b1) != 0  # 8 bits

            flags = reader.read_ui8()
            # 5bits skipped
            no_close = (flags & 0b100) != 0  # 6bits
            end_cap_style = flags & 0b11  # 8bits

            miter_limit_factor = reader.read_ui16() if join_style == 2 else None

            if not has_fill_flag:
                color = Color.read_rgba(reader)
                fill_type = None
            else:
                fill_type = FillStyle.read(reader, version)
                color = None

            line_style_array.append(
                cls(
                    width=width,
                    color=color,
                    start_cap_style=start_cap_style,
                    join_style=join_style,
                    has_fill_flag=has_fill_flag,
                    no_h_scale_flag=no_h_scale_flag,
                    no_v_scale_flag=no_v_scale_flag,
                    pixel_hinting_flag=pixel_hinting_flag,
                    no_close=no_close,
                    end_cap_style=end_cap_style,
                    miter_limit_factor=miter_limit_factor,
                    fill_type=fill_type,
                )
            )

        return line_style_array
