"""
Minimal XML element tree, standing in for PHP's `SimpleXMLElement`.

Only what the SVG builder needs: append a child, append an attribute, serialise. Attributes keep
insertion order, so the output reads like ArakneSwf's. `xml.etree.ElementTree` would work too, but
it reorders namespace declarations and escapes attribute values differently, and the SVG builder
depends on element *order* being exactly PHP's.
"""

from __future__ import annotations

_ESCAPES = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})


class XmlElement:
    """An XML element: a tag, ordered attributes and ordered children."""

    __slots__ = ("attributes", "children", "tag")

    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.attributes: dict[str, str] = {}
        self.children: list[XmlElement] = []

    def add_child(self, tag: str) -> XmlElement:
        """Append a child element and return it."""
        child = XmlElement(tag)
        self.children.append(child)

        return child

    def add_attribute(self, name: str, value: str) -> None:
        """Append an attribute. A repeated name is ignored, as `SimpleXMLElement` does."""
        if name not in self.attributes:
            self.attributes[name] = value

    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute, replacing any previous value."""
        self.attributes[name] = value

    def to_xml(self) -> str:
        """Serialise as a standalone document, with the XML declaration."""
        return '<?xml version="1.0"?>\n' + self._serialize()

    def _serialize(self) -> str:
        parts = ["<", self.tag]

        for name, value in self.attributes.items():
            parts.append(f' {name}="{value.translate(_ESCAPES)}"')

        if not self.children:
            parts.append("/>")

            return "".join(parts)

        parts.append(">")
        parts.extend(child._serialize() for child in self.children)
        parts.append(f"</{self.tag}>")

        return "".join(parts)
