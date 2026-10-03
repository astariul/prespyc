"""The root SVG canvas."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.drawer.svg.base_svg_canvas import BaseSvgCanvas
from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder
from prespyc.extractor.drawer.svg.xml import XmlElement

if TYPE_CHECKING:
    from prespyc.parser.structure.record.rectangle import Rectangle


class SvgCanvas(BaseSvgCanvas):
    """Draws a character into a standalone SVG document."""

    __slots__ = ("_defs_element", "_last_id", "_root", "scale", "subpixel_stroke_width")

    def __init__(self, bounds: Rectangle, subpixel_stroke_width: bool = True, scale: float = 1.0) -> None:
        root = XmlElement("svg")
        root.add_attribute("xmlns", "http://www.w3.org/2000/svg")
        root.add_attribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.add_attribute("width", f"{num(bounds.width / 20)}px")
        root.add_attribute("height", f"{num(bounds.height / 20)}px")

        self._root = root
        self._defs_element: XmlElement | None = None
        self._last_id = 0

        self.subpixel_stroke_width = subpixel_stroke_width
        """
        Whether strokes keep their real, possibly sub-pixel, SWF width.

        When true, a stroke thinner than a pixel is left to the renderer's antialiasing, so it comes
        out faint — which is *not* what Flash does, as Flash always draws a stroke at least one pixel
        wide. When false, `render()` widens every stroke to one pixel of the output.
        """

        self.scale = scale
        """Pixels of the output per pixel of the drawing, i.e. what a resizer scales it by."""

        super().__init__(SvgBuilder(root))

    @property
    def root(self) -> XmlElement:
        """The root `<svg>` element, so a caller can adjust its attributes before rendering."""
        return self._root

    def render(self) -> str:
        if not self.subpixel_stroke_width:
            _widen_strokes(self._root, self.scale)

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


def _widen_strokes(root: XmlElement, scale: float) -> None:
    """
    Widen every stroke to at least one pixel of the output.

    `stroke-width` is in the user units of its path, which the chain of `<use>` matrices placing it
    scales up or down: a floor in user units would be too thick for what is scaled up and too thin
    for what is scaled down, so the chain is walked to turn one output pixel into user units. Every
    included object sits in `<defs>` under its own id, referenced by one `<use>`: the references form
    a tree, walked from the root.
    """
    by_id: dict[str, XmlElement] = {}
    pending = [root]

    while pending:
        element = pending.pop()
        id = element.attributes.get("id")

        if id is not None:
            by_id[id] = element

        pending += element.children

    def walk(element: XmlElement, scale: float) -> None:
        transform = element.attributes.get("transform")

        if transform is not None and transform.startswith("matrix("):
            a, b, c, d = (float(value) for value in transform[7 : transform.index(")")].split(",")[:4])
            scale *= math.sqrt(abs(a * d - b * c))

        if scale == 0 or element.tag == "clipPath":
            # Nothing is drawn under a degenerate matrix, and a clip path is a silhouette.
            return

        if element.tag == "use":
            target = by_id.get(element.attributes.get("xlink:href", "")[1:])

            if target is not None:
                walk(target, scale)

            return

        width = element.attributes.get("stroke-width")

        if element.tag == "path" and width is not None and float(width) < 1 / scale:
            element.set_attribute("stroke-width", num(1 / scale))

        for child in element.children:
            if child.tag != "defs":
                walk(child, scale)

    walk(root, scale)
