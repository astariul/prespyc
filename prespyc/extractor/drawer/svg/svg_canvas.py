"""The root SVG canvas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.drawer.svg.base_svg_canvas import BaseSvgCanvas
from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder
from prespyc.extractor.drawer.svg.xml import XmlElement

if TYPE_CHECKING:
    from prespyc.parser.structure.record.rectangle import Rectangle


class SvgCanvas(BaseSvgCanvas):
    """Draws a character into a standalone SVG document."""

    __slots__ = ("_defs_element", "_last_id", "_root")

    def __init__(self, bounds: Rectangle, subpixel_stroke_width: bool = True) -> None:
        root = XmlElement("svg")
        root.add_attribute("xmlns", "http://www.w3.org/2000/svg")
        root.add_attribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.add_attribute("width", f"{num(bounds.width / 20)}px")
        root.add_attribute("height", f"{num(bounds.height / 20)}px")

        self._root = root
        self._defs_element: XmlElement | None = None
        self._last_id = 0

        super().__init__(SvgBuilder(root, subpixel_stroke_width))

    @property
    def root(self) -> XmlElement:
        """The root `<svg>` element, so a caller can adjust its attributes before rendering."""
        return self._root

    def render(self) -> str:
        return self.to_xml()

    def to_xml(self) -> str:
        """The SVG document as an XML string."""
        return self._root.to_xml()

    def _next_object_id(self) -> str:
        id = f"object-{self._last_id}"
        self._last_id += 1

        return id

    def _defs(self) -> XmlElement:
        if self._defs_element is None:
            self._defs_element = self._root.add_child("defs")

        return self._defs_element

    def _new_group(self, builder: SvgBuilder, bounds: Rectangle) -> XmlElement:
        return builder.add_group(bounds)

    def _new_group_with_offset(self, builder: SvgBuilder, offset_x: int, offset_y: int) -> XmlElement:
        return builder.add_group_with_offset(offset_x, offset_y)
