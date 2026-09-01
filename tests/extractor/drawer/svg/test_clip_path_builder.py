"""Translated from ArakneSwf's `tests/Extractor/Drawer/Svg/ClipPathBuilderTest.php`."""

from __future__ import annotations

import pytest

from prespyc.extractor.drawer.svg.clip_path_builder import ClipPathBuilder
from prespyc.extractor.drawer.svg.svg_builder import SvgBuilder
from prespyc.extractor.drawer.svg.xml import XmlElement
from prespyc.parser.structure.record.matrix import Matrix
from prespyc.swf_file import SwfFile
from tests.support import assert_svg_equals, fixture


@pytest.fixture
def root_and_builder():
    root = XmlElement("svg")
    root.add_attribute("xmlns", "http://www.w3.org/2000/svg")
    clip_path = root.add_child("clipPath")

    return root, ClipPathBuilder(clip_path, SvgBuilder(root))


def test_does_nothing_on_unsupported_characters(root_and_builder):
    root, builder = root_and_builder
    extractor = SwfFile(fixture("extractor", "mob-leponge", "mob-leponge.swf")).extractor

    extractor.character(1).draw(builder)  # An image

    builder.start_clip(extractor.character(1), Matrix(), 0)
    builder.end_clip("")

    assert builder.render() is None
    assert len(root.children) == 1
    assert root.children[0].children == []


def test_build_with_sprite(root_and_builder):
    root, builder = root_and_builder
    extractor = SwfFile(fixture("extractor", "mob-leponge", "mob-leponge.swf")).extractor

    extractor.character(4).draw(builder)  # A sprite

    builder.start_clip(extractor.character(1), Matrix(), 0)
    builder.end_clip("")

    assert builder.render() is None
    assert_svg_equals(
        root.to_xml(),
        """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg">
            <clipPath>
                <path fill-rule="evenodd" fill="url(#gradient-R63dfb90eb595e9795bdd21b4fefc7c4b)" stroke="none" d="M5.15 0Q5.15 2.15 3.65 3.65Q2.15 5.15 0 5.15Q-2.15 5.15 -3.65 3.65Q-5.15 2.15 -5.15 0Q-5.15 -2.15 -3.65 -3.65Q-2.15 -5.15 0 -5.15Q2.15 -5.15 3.65 -3.65Q5.15 -2.15 5.15 0" transform="matrix(1, 0, 0, 1, -5.15, -5.15) translate(5.15,5.15)"/>
            </clipPath>
            <radialGradient gradientTransform="matrix(0.0068, 0, 0, 0.0068, 0, 0)" gradientUnits="userSpaceOnUse" spreadMethod="pad" id="gradient-R63dfb90eb595e9795bdd21b4fefc7c4b" cx="0" cy="0" r="819.2">
                <stop offset="0" stop-color="#99795a"/>
                <stop offset="0.44705882352941" stop-color="#99734f" stop-opacity="0.43137254901961"/>
                <stop offset="0.83137254901961" stop-color="#9c6e44" stop-opacity="0"/>
            </radialGradient>
        </svg>""",
    )


def test_build_clip_path_with_shape(root_and_builder):
    root, builder = root_and_builder
    extractor = SwfFile(fixture("extractor", "mob-leponge", "mob-leponge.swf")).extractor

    extractor.character(12).draw(builder)  # A shape

    assert_svg_equals(
        root.to_xml(),
        """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg">
            <clipPath>
                <path fill-rule="evenodd" fill="#704d00" stroke="none" d="M1.25 -1.05L4.3 -0.05L4.7 1.6L2.55 2.45L-0.3 1.85L-1.45 0.75L-1.05 -0.5L1.25 -1.05" transform="translate(1.45,1.05)"/><path fill="none" stroke="#000000" stroke-opacity="0.30196078431373" stroke-width="0.05" stroke-linecap="round" stroke-linejoin="round" d="M1.25 -1.05L-1.05 -0.5L-1.45 0.75L-0.3 1.85L2.55 2.45L4.7 1.6L4.3 -0.05L1.25 -1.05" transform="translate(1.45,1.05)"/>
            </clipPath>
        </svg>""",
    )


def test_ignores_zero_width_stroke(root_and_builder):
    root, builder = root_and_builder
    extractor = SwfFile(fixture("extractor", "morphshape", "a3.swf")).extractor

    extractor.character(569).draw(builder)  # A morph shape

    assert_svg_equals(
        root.to_xml(),
        """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg">
            <clipPath>
                <path d="M-63.9 15.75L-60.6 16.85L-56.25 17.75L-44.35 19L-35.35 19.35L-32.15 19.4L-23.35 19.4L-13.4 19.3L-7 19.1L0.6 18.75L3.05 18.65L12.2 18Q30.05 16.65 41.65 14.35L55.75 11.1Q61.3 9.6 65.75 7.95Q68.3 7 69.35 5.9Q72.25 2.9 63.6 -1.25Q59.95 -2.65 57.9 -4.65Q56.85 -5.65 56.25 -6.8Q52.95 -13.05 48.7 -18.4Q44.1 -24.15 38.4 -28.95Q34.75 -32.05 30.6 -34.7Q26.45 -37.4 22.15 -39.4Q9.25 -45.4 -5.1 -45.55L-14.05 -45.1Q-27.5 -43.6 -37.95 -36.7Q-44.6 -32.35 -48.5 -23.75Q-51.55 -17 -52.85 -7.65L-53.6 -0.3Q-54.65 3.1 -60.15 5.85L-64.35 8.5Q-67.65 11.05 -66.85 13.15Q-66.3 14.55 -63.9 15.75" fill="#d6fff6" fill-opacity="0.10196078431373" fill-rule="evenodd" stroke="none" transform="translate(67,45.55)"/>
            </clipPath>
        </svg>""",
    )
