"""
Phase 6 gate: real Dofus SWFs render to WEBP + JSON that matches noxine's schema.

`tests/fixtures/extractor/` holds genuine Dofus Retro gfx files (1047, 1305, 1435, 1601, 1597,
1700, o3, 7022), so these exercise the whole parse → extract → SVG → raster → atlas chain.
"""

from __future__ import annotations

import io
import json

import pytest
from PIL import Image

import prespyc
from prespyc.output.exporter import build_spritesheet
from tests.support import fixture


def assert_matches_noxine_schema(data: dict, page_name: str, zoom: float, main_page: bool) -> None:
    """The schema noxine's `SpriteLoader` consumes. Keep in sync with `scripts/spritesheet.py`."""
    assert set(data) <= {"frames", "meta", "flash_frames", "animations"}
    assert set(data) >= {"frames", "meta"}

    meta = data["meta"]
    assert meta["app"] == "noxine"
    assert meta["image"] == f"{page_name}.webp"
    assert meta["format"] == "RGBA8888"
    assert meta["scale"] == zoom
    assert set(meta["size"]) == {"w", "h"}
    assert meta["size"]["w"] > 0 and meta["size"]["h"] > 0

    assert data["frames"], "a spritesheet with no frame is useless"

    for key, frame in data["frames"].items():
        assert key.isdigit()
        assert set(frame) == {"frame", "rotated", "trimmed", "spriteSourceSize", "sourceSize", "anchor"}
        assert set(frame["frame"]) == {"x", "y", "w", "h"}
        assert set(frame["spriteSourceSize"]) == {"x", "y", "w", "h"}
        assert set(frame["sourceSize"]) == {"w", "h"}
        assert set(frame["anchor"]) == {"x", "y"}
        assert frame["rotated"] is False
        assert frame["trimmed"] is False
        assert frame["frame"]["w"] == frame["sourceSize"]["w"]
        assert frame["frame"]["h"] == frame["sourceSize"]["h"]
        assert frame["frame"]["x"] + frame["frame"]["w"] <= meta["size"]["w"]
        assert frame["frame"]["y"] + frame["frame"]["h"] <= meta["size"]["h"]

    if main_page:
        assert data["flash_frames"]
    else:
        assert "flash_frames" not in data


def test_export_a_dofus_sprite_by_name(tmp_path):
    written = prespyc.export(fixture("extractor", "1047", "1047.swf"), "anim0R", tmp_path, zoom=2)

    assert [path.name for path in written] == ["anim0R.webp", "anim0R.json"]

    data = json.loads((tmp_path / "anim0R.json").read_text())
    assert_matches_noxine_schema(data, "anim0R", zoom=2, main_page=True)

    # anim0R has one frame of its own but 40 through its children, which is what animates
    assert len(data["frames"]) == 40
    assert data["flash_frames"] == [{"frames": list(range(40))}]

    with Image.open(tmp_path / "anim0R.webp") as image:
        assert image.format == "WEBP"
        assert (image.width, image.height) == (data["meta"]["size"]["w"], data["meta"]["size"]["h"])


def test_export_by_character_id(tmp_path):
    written = prespyc.export(fixture("extractor", "1047", "1047.swf"), 65, tmp_path, name="65")

    assert [path.name for path in written] == ["65.webp", "65.json"]
    assert_matches_noxine_schema(json.loads((tmp_path / "65.json").read_text()), "65", zoom=1.0, main_page=True)


def test_zoom_scales_the_frames(tmp_path):
    small = json.loads(
        (prespyc.export(fixture("extractor", "1047", "1047.swf"), 65, tmp_path / "x1", name="s")[1]).read_text()
    )
    large = json.loads(
        (prespyc.export(fixture("extractor", "1047", "1047.swf"), 65, tmp_path / "x2", name="s", zoom=2)[1]).read_text()
    )

    assert large["frames"]["0"]["frame"]["w"] == pytest.approx(small["frames"]["0"]["frame"]["w"] * 2, abs=2)
    assert large["meta"]["scale"] == 2

    # The anchor is a fraction of the frame, so it does not move with the zoom
    assert large["frames"]["0"]["anchor"] == pytest.approx(small["frames"]["0"]["anchor"])


def test_anchor_places_the_origin(tmp_path):
    swf = prespyc.open(fixture("extractor", "1047", "1047.swf"))
    drawable = swf.extractor["anim0R"]
    sheet = build_spritesheet(drawable, "anim0R", zoom=2)

    bounds = drawable.bounds
    page = sheet.pack()[0]
    anchor = page.data["frames"]["0"]["anchor"]

    assert anchor["x"] == pytest.approx(-bounds.xmin / bounds.width)
    assert anchor["y"] == pytest.approx(-bounds.ymin / bounds.height)


@pytest.mark.parametrize(
    ("swf", "selector"),
    [
        (("1305", "1305.swf"), "anim0R"),
        (("1435", "1435.swf"), "anim0R"),
        (("1601", "1601.swf"), "anim0R"),
        (("1597", "1597.swf"), 48),
        (("o3", "o3.swf"), 31),
        (("7022", "7022.swf"), 5),
    ],
)
def test_export_real_dofus_gfx(swf, selector, tmp_path):
    written = prespyc.export(fixture("extractor", *swf), selector, tmp_path, zoom=2, name="out")

    data = json.loads((tmp_path / "out.json").read_text())
    assert_matches_noxine_schema(data, "out", zoom=2, main_page=True)

    for path in written:
        assert path.stat().st_size > 0

    # Every frame must actually contain something
    with Image.open(tmp_path / "out.webp") as page:
        assert page.getbbox() is not None


def test_multi_page_export_links_the_pages(tmp_path):
    swf = prespyc.open(fixture("extractor", "1047", "1047.swf"))
    sheet = build_spritesheet(swf.extractor["anim0R"], "anim0R", zoom=2)

    # A tiny page limit forces the split, without needing a huge sprite
    written = sheet.write(tmp_path, max_size=128)
    names = [path.name for path in written]

    assert len(names) > 2
    assert names[0] == "anim0R.webp"

    main = json.loads((tmp_path / "anim0R.json").read_text())
    assert main["meta"]["related_multi_packs"]
    assert_matches_noxine_schema(main, "anim0R", zoom=2, main_page=True)

    seen = set(main["frames"])

    for related in main["meta"]["related_multi_packs"]:
        page_name = related.removesuffix(".json")
        data = json.loads((tmp_path / related).read_text())
        assert_matches_noxine_schema(data, page_name, zoom=2, main_page=False)
        assert not seen & set(data["frames"]), "a frame must live on exactly one page"
        seen |= set(data["frames"])

    assert sorted(int(i) for i in seen) == list(range(40))


def test_webp_is_smaller_than_the_equivalent_png(tmp_path):
    """The reason the output format changed. Guards against a lossless/quality regression."""
    swf = prespyc.open(fixture("extractor", "1047", "1047.swf"))
    page = build_spritesheet(swf.extractor["anim0R"], "anim0R", zoom=2).pack()[0]

    webp = io.BytesIO()
    page.image.save(webp, format="WEBP", quality=90, method=6)

    png = io.BytesIO()
    page.image.save(png, format="PNG", optimize=True)

    assert webp.tell() < png.tell()
