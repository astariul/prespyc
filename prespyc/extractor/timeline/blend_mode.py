"""Blend modes of a display list object."""

from __future__ import annotations

from enum import IntEnum


class BlendMode(IntEnum):
    """How a display list object is composited with what is already drawn."""

    NORMAL = 1
    LAYER = 2
    MULTIPLY = 3
    SCREEN = 4
    LIGHTEN = 5
    DARKEN = 6
    DIFFERENCE = 7
    ADD = 8
    SUBTRACT = 9
    INVERT = 10
    ALPHA = 11
    ERASE = 12
    OVERLAY = 13
    HARDLIGHT = 14

    @property
    def css_value(self) -> str | None:
        """
        Matching CSS `mix-blend-mode` value, or `None` when the mode has no CSS equivalent or is
        the default.
        """
        return _CSS_VALUES.get(self)


_CSS_VALUES: dict[BlendMode, str] = {
    BlendMode.MULTIPLY: "multiply",
    BlendMode.SCREEN: "screen",
    BlendMode.LIGHTEN: "lighten",
    BlendMode.ADD: "lighten",
    BlendMode.DARKEN: "darken",
    BlendMode.SUBTRACT: "darken",
    BlendMode.DIFFERENCE: "difference",
    BlendMode.OVERLAY: "overlay",
    BlendMode.HARDLIGHT: "hard-light",
}
