"""Filling the `d` attribute of an SVG `<path>`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc._util import num

if TYPE_CHECKING:
    from prespyc.extractor.drawer.svg.xml import XmlElement


class SvgPathDrawer:
    """
    Draws one path into the `d` attribute of an SVG element.

    Coordinates come in as twips and go out as pixels.
    """

    __slots__ = ("_d", "_element")

    def __init__(self, element: XmlElement) -> None:
        self._element = element
        self._d = ""

    def move(self, x: int, y: int) -> None:
        self._d += f"M{num(x / 20)} {num(y / 20)}"

    def line(self, to_x: int, to_y: int) -> None:
        self._d += f"L{num(to_x / 20)} {num(to_y / 20)}"

    def curve(self, control_x: int, control_y: int, to_x: int, to_y: int) -> None:
        self._d += f"Q{num(control_x / 20)} {num(control_y / 20)} {num(to_x / 20)} {num(to_y / 20)}"

    def draw(self) -> None:
        self._element.add_attribute("d", self._d)
        self._d = ""
