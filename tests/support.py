"""Shared test helpers: fixture paths, golden comparison, SWF building."""

from __future__ import annotations

import io
import struct
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path

from prespyc.errors import Errors

FIXTURES = Path(__file__).parent / "fixtures"
"""Root of the fixture tree, mirroring ArakneSwf's `tests/**/Fixtures`."""


def fixture(*parts: str) -> Path:
    """Path of a fixture file, e.g. `fixture("extractor", "1047", "1047.swf")`."""
    path = FIXTURES.joinpath(*parts)
    assert path.exists(), f"missing fixture: {path}"

    return path


# --------------------------------------------------------------------------------------- XML / SVG


def canonical_xml(text: str | bytes) -> str:
    """
    Normalize an XML document for comparison: attribute order, insignificant whitespace and
    namespace prefixes are ignored, text content is not.

    This is the Python counterpart of PHPUnit's `assertXmlStringEqualsXmlString`.
    """
    if isinstance(text, str):
        text = text.encode("utf-8")

    root = ET.fromstring(text)
    out = io.StringIO()
    _write_canonical(root, out)

    return out.getvalue()


def _write_canonical(element: ET.Element, out: io.StringIO) -> None:
    out.write("<" + element.tag)

    for name in sorted(element.attrib):
        out.write(f" {name}={element.attrib[name]!r}")

    children = list(element)
    text = (element.text or "").strip()

    if not children and not text:
        out.write("/>")
        return

    out.write(">")

    if text:
        out.write(text)

    for child in children:
        _write_canonical(child, out)
        tail = (child.tail or "").strip()
        if tail:
            out.write(tail)

    out.write("</" + element.tag + ">")


def assert_svg_equals(actual: str, expected: str) -> None:
    """Assert two SVG documents are equivalent, ignoring formatting and attribute order."""
    assert canonical_xml(actual) == canonical_xml(expected)


def assert_svg_matches(actual: str, golden: Path | str) -> None:
    """Assert an SVG document matches a golden file."""
    path = Path(golden)
    assert path.exists(), f"missing golden: {path}"

    if canonical_xml(actual) != canonical_xml(path.read_bytes()):
        _save_failed(path.name, actual.encode("utf-8"))
        raise AssertionError(f"SVG does not match golden {path}")


# ------------------------------------------------------------------------------------------ Images


def image_diff(actual: bytes, expected: bytes, compare_size: bool = True) -> float:
    """
    Difference ratio between two encoded images, as the mean absolute per-channel RGBA difference.

    0.0 means pixel-identical.
    """
    from PIL import Image

    a = Image.open(io.BytesIO(actual)).convert("RGBA")
    b = Image.open(io.BytesIO(expected)).convert("RGBA")

    if compare_size and a.size != b.size:
        raise AssertionError(f"Image size differ. Expected: {b.size[0]}x{b.size[1]} Actual: {a.size[0]}x{a.size[1]}")

    if a.size != b.size:
        b = b.resize(a.size)

    pa = a.tobytes()
    pb = b.tobytes()

    return sum(abs(x - y) for x, y in zip(pa, pb)) / (len(pa) * 255)


def assert_image_matches(actual: bytes, golden: Path | str, delta: float = 0.0) -> None:
    """Assert an encoded image matches a golden file, within a difference ratio."""
    path = Path(golden)
    assert path.exists(), f"missing golden: {path}"

    diff = image_diff(actual, path.read_bytes())

    if diff > delta:
        _save_failed(path.name, actual)
        raise AssertionError(f"The images are different (diff ratio: {diff})")


def _save_failed(name: str, blob: bytes) -> None:
    """Dump a mismatching result under `reports/` so it can be diffed by hand."""
    directory = Path(__file__).parent.parent / "reports" / "failed"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_bytes(blob)


# ------------------------------------------------------------------------------------- SWF reading


def fixture_reader(path: Path | str, offset: int | None = None, errors: int = Errors.ALL):
    """
    Reader positioned on the body of a SWF fixture, decompressing it when needed.

    Port of ArakneSwf's `ParserTestCase::createReader()`.
    """
    from prespyc.parser.reader import Reader

    data = Path(path).read_bytes()
    reader = Reader(data, errors=errors)
    compressed = data[0:1] == b"C"

    if compressed:
        reader.skip_bytes(8)
        reader = reader.uncompress()

    if offset is not None:
        reader.skip_bytes(offset - (8 if compressed else 0))

    return reader


class SwfBuilder:
    """
    Builds minimal SWF files from raw tag data.

    Port of ArakneSwf's `tests/SwfBuilder.php`. Tags are `(code, body)` pairs; the body defaults to
    empty.
    """

    def __init__(self) -> None:
        self._temp_files: list[Path] = []

    def create_swf_file(self, tags: Sequence[tuple[int, bytes] | tuple[int]], errors: int = Errors.ALL):
        from prespyc.swf_file import SwfFile

        handle, name = tempfile.mkstemp(prefix="swf", suffix=".swf")
        path = Path(name)
        self._temp_files.append(path)

        with open(handle, "wb") as file:
            file.write(self.build_swf(tags))

        return SwfFile(path, errors=errors)

    def build_swf(self, tags: Sequence[tuple[int, bytes] | tuple[int]]) -> bytes:
        body = self.build_tags(tags) + b"\x00\x00"  # End of tags

        return b"FWS\x05" + struct.pack("<I", len(body) + 8) + b"\x00\x01\x00\x01\x00" + body

    def build_tags(self, tags: Sequence[tuple[int, bytes] | tuple[int]]) -> bytes:
        body = bytearray()

        for params in tags:
            code = params[0]
            content = params[1] if len(params) > 1 else b""
            length = len(content)

            if length < 0x3F:
                body += struct.pack("<H", length | (code << 6))
            else:
                body += struct.pack("<HI", 0x3F | (code << 6), length)

            body += content

        return bytes(body)

    def cleanup(self) -> None:
        for path in self._temp_files:
            path.unlink(missing_ok=True)
        self._temp_files.clear()
