"""Translated from ArakneSwf's `tests/Extractor/Shape/Svg/SvgPathDrawerTest.php`."""

from __future__ import annotations

from prespyc.extractor.drawer.svg.svg_path_drawer import SvgPathDrawer
from prespyc.extractor.drawer.svg.xml import XmlElement


def test_path_drawer_writes_the_d_attribute():
    element = XmlElement("path")
    drawer = SvgPathDrawer(element)

    drawer.move(10, 20)
    drawer.line(30, 40)
    drawer.curve(50, 60, 70, 80)
    drawer.line(90, 100)
    drawer.line(110, 110)
    drawer.draw()

    assert element.attributes["d"] == "M0.5 1L1.5 2Q2.5 3 3.5 4L4.5 5L5.5 5.5"
    assert element.to_xml() == '<?xml version="1.0"?>\n<path d="M0.5 1L1.5 2Q2.5 3 3.5 4L4.5 5L5.5 5.5"/>'
