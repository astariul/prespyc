"""Atlas packing and the PixiJS JSON schema."""

from __future__ import annotations

import json

import pytest
from PIL import Image

from prespyc.output.spritesheet import MAX_ATLAS_SIZE, Spritesheet, plan_pages


def frames(count: int, size: tuple[int, int] = (30, 20)) -> list[Image.Image]:
    return [Image.new("RGBA", size, (255, 0, 0, 128)) for _ in range(count)]


def test_plan_pages_empty():
    assert plan_pages([], 1, MAX_ATLAS_SIZE) == (1, [[]])


def test_plan_pages_is_square_ish():
    cols, pages = plan_pages([(30, 20)] * 9, 1, MAX_ATLAS_SIZE)

    assert cols == 3
    assert pages == [list(range(9))]


def test_plan_pages_splits_when_a_page_would_overflow():
    cols, pages = plan_pages([(4000, 4000)] * 10, 1, 8192)

    assert cols == 2
    assert pages == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    assert sum(len(page) for page in pages) == 10


def test_plan_pages_never_exceeds_max_size():
    cols, pages = plan_pages([(5000, 300)] * 40, 1, 8192)

    assert cols * 5001 <= 8192
    for page in pages:
        rows = -(-len(page) // cols)
        assert rows * 301 <= 8192


def test_pack_single_page():
    sheet = Spritesheet("1964", frames=frames(4), bounds=(-10.0, -5.0, 20.0, 15.0), zoom=2)
    pages = sheet.pack()

    assert len(pages) == 1
    page = pages[0]

    assert page.name == "1964"
    assert page.data["meta"]["image"] == "1964.webp"
    assert page.data["meta"]["format"] == "RGBA8888"
    assert page.data["meta"]["scale"] == 2
    assert page.data["meta"]["size"] == {"w": page.image.width, "h": page.image.height}
    assert "related_multi_packs" not in page.data["meta"]
    assert sorted(page.data["frames"]) == ["0", "1", "2", "3"]

    # The anchor is where (0, 0) sits inside the bounds, as a fraction of the size
    assert page.data["frames"]["0"]["anchor"] == pytest.approx({"x": 10 / 30, "y": 5 / 20})


def test_pack_multiple_pages_links_them():
    sheet = Spritesheet("1964", frames=frames(10, (4000, 4000)))
    pages = sheet.pack(max_size=8192)

    assert [page.name for page in pages] == ["1964", "1964-1", "1964-2"]
    assert pages[0].data["meta"]["related_multi_packs"] == ["1964-1.json", "1964-2.json"]

    # Extra pages carry frames only
    for page in pages[1:]:
        assert "related_multi_packs" not in page.data["meta"]
        assert "flash_frames" not in page.data

    # Frame indices stay global, so flash_frames keeps referencing them unchanged
    assert sorted(int(i) for page in pages for i in page.data["frames"]) == list(range(10))


def test_frames_do_not_overlap():
    sheet = Spritesheet("s", frames=frames(6, (10, 10)))
    page = sheet.pack(margin=1)[0]

    boxes = [f["frame"] for f in page.data["frames"].values()]

    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            overlaps_x = a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            overlaps_y = a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]
            assert not (overlaps_x and overlaps_y)


def test_write(tmp_path):
    sheet = Spritesheet("1964", frames=frames(2), flash_frames=[{"frames": [0, 1]}], zoom=2)
    written = sheet.write(tmp_path)

    assert [path.name for path in written] == ["1964.webp", "1964.json"]

    with Image.open(tmp_path / "1964.webp") as image:
        assert image.format == "WEBP"

    data = json.loads((tmp_path / "1964.json").read_text())
    assert data["flash_frames"] == [{"frames": [0, 1]}]


def test_zero_size_bounds_give_a_zero_anchor():
    sheet = Spritesheet("s", frames=frames(1), bounds=(0, 0, 0, 0))
    page = sheet.pack()[0]

    assert page.data["frames"]["0"]["anchor"] == {"x": 0, "y": 0}
