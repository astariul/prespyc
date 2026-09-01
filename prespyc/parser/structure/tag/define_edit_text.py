"""DefineEditText tag."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.edit_text_layout import EditTextLayout
from prespyc.parser.structure.record.rectangle import Rectangle

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineEditTextTag:
    """A dynamic (editable) text field character."""

    TYPE: ClassVar[int] = 37

    character_id: int
    bounds: Rectangle
    word_wrap: bool
    multiline: bool
    password: bool
    read_only: bool
    auto_size: bool
    no_select: bool
    border: bool
    was_static: bool
    html: bool
    use_outlines: bool
    font_id: int | None
    font_class: bytes | None
    font_height: int | None
    text_color: Color | None
    max_length: int | None
    layout: EditTextLayout | None
    variable_name: bytes
    initial_text: bytes | None

    @classmethod
    def read(cls, reader: Reader) -> Self:
        """Read a DefineEditText tag."""
        character_id = reader.read_ui16()
        bounds = Rectangle.read(reader)

        flags = reader.read_ui8()
        has_text = (flags & 0b10000000) == 0b10000000
        word_wrap = (flags & 0b01000000) == 0b01000000
        multiline = (flags & 0b00100000) == 0b00100000
        password = (flags & 0b00010000) == 0b00010000
        read_only = (flags & 0b00001000) == 0b00001000
        has_text_color = (flags & 0b00000100) == 0b00000100
        has_max_length = (flags & 0b00000010) == 0b00000010
        has_font = (flags & 0b00000001) == 0b00000001

        flags = reader.read_ui8()
        has_font_class = (flags & 0b10000000) == 0b10000000
        auto_size = (flags & 0b01000000) == 0b01000000
        has_layout = (flags & 0b00100000) == 0b00100000
        no_select = (flags & 0b00010000) == 0b00010000
        border = (flags & 0b00001000) == 0b00001000
        was_static = (flags & 0b00000100) == 0b00000100
        html = (flags & 0b00000010) == 0b00000010
        use_outlines = (flags & 0b00000001) == 0b00000001

        return cls(
            character_id=character_id,
            bounds=bounds,
            word_wrap=word_wrap,
            multiline=multiline,
            password=password,
            read_only=read_only,
            auto_size=auto_size,
            no_select=no_select,
            border=border,
            was_static=was_static,
            html=html,
            use_outlines=use_outlines,
            font_id=reader.read_ui16() if has_font else None,
            font_class=reader.read_null_terminated_string() if has_font_class else None,
            font_height=reader.read_ui16() if has_font else None,
            text_color=Color.read_rgba(reader) if has_text_color else None,
            max_length=reader.read_ui16() if has_max_length else None,
            layout=EditTextLayout.read(reader) if has_layout else None,
            variable_name=reader.read_null_terminated_string(),
            initial_text=reader.read_null_terminated_string() if has_text else None,
        )
