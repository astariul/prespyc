"""
Atlas packing: sprite frames to WEBP pages plus PixiJS-compatible JSON.

Port of noxine's `scripts/spritesheet.py`, emitting WEBP instead of PNG. The JSON schema is
unchanged, so PixiJS consumption is identical.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

MAX_ATLAS_SIZE = 8192
"""
Maximum width/height in pixels of a single atlas page.

GPUs reject textures larger than their `MAX_TEXTURE_SIZE` (commonly 16384 on desktop, as low as
4096-8192 elsewhere) with `texImage2D: width or height out of range`. 8192 keeps every page
uploadable on the vast majority of devices; sprites whose frames do not fit on one page are split
across several, linked through `meta.related_multi_packs`.
"""


def plan_pages(sizes: list[tuple[int, int]], margin: int, max_size: int) -> tuple[int, list[list[int]]]:
    """
    Decide how to split frames across atlas pages so that no page exceeds `max_size`.

    Frames of a sprite are near-uniform in size, so a uniform grid sized from the largest frame is
    enough to keep every page within the limit.

    Returns `(cols, pages)`, where `cols` is the number of columns used on every page and `pages`
    holds, for each page, the global frame indices laid out on it, in order.
    """
    n = len(sizes)

    if n == 0:
        return 1, [[]]

    max_fw = max(w for w, _ in sizes) + margin
    max_fh = max(h for _, h in sizes) + margin

    # Square-ish, but never wide or tall enough for a page to exceed `max_size`.
    cols = max(1, min(math.ceil(math.sqrt(n)), max_size // max_fw))
    rows_per_page = max(1, max_size // max_fh)
    frames_per_page = max(1, cols * rows_per_page)

    pages = [list(range(start, min(start + frames_per_page, n))) for start in range(0, n, frames_per_page)]

    return cols, pages


@dataclass(frozen=True, slots=True)
class Page:
    """One atlas page: a WEBP image and its JSON descriptor."""

    name: str
    image: Image.Image
    data: dict

    def write(self, out_dir: Path | str, quality: int = 90, lossless: bool = False) -> tuple[Path, Path]:
        """Write `{name}.webp` and `{name}.json` into `out_dir`, and return both paths."""
        directory = Path(out_dir)
        directory.mkdir(parents=True, exist_ok=True)

        image_path = directory / f"{self.name}.webp"
        json_path = directory / f"{self.name}.json"

        self.image.save(image_path, format="WEBP", quality=quality, lossless=lossless, method=6)
        json_path.write_text(json.dumps(self.data), encoding="utf-8")

        return image_path, json_path


@dataclass
class Spritesheet:
    """
    A sprite's frames, ready to be packed into atlas pages.

    `bounds` is the sprite bounding box in *output* pixels (i.e. twips / 20 * zoom) and gives the
    anchor; `flash_frames` and `animations` are the timeline metadata the client plays back.
    """

    name: str
    """Base name of the pages, i.e. the exported id."""

    frames: list[Image.Image] = field(default_factory=list)
    bounds: tuple[float, float, float, float] = (0, 0, 0, 0)
    """`(xmin, ymin, xmax, ymax)` of the sprite, in output pixels."""

    flash_frames: list[dict] = field(default_factory=list)
    animations: dict[str, list[int]] = field(default_factory=dict)
    zoom: float = 1.0

    def pack(self, margin: int = 1, max_size: int = MAX_ATLAS_SIZE) -> list[Page]:
        """
        Pack the frames into one or more atlas pages.

        The first page is the main one, named `{name}`: it carries the shared
        `flash_frames`/`animations` metadata and, when there is more than one page, a
        `meta.related_multi_packs` list pointing at the others. Extra pages, named `{name}-1`,
        `{name}-2`, …, hold only their frames. Frame indices stay global across pages, so
        `flash_frames`/`animations` keep referencing them unchanged.
        """
        from PIL import Image

        sizes = [(image.width, image.height) for image in self.frames]
        cols, pages = plan_pages(sizes, margin, max_size)
        n_pages = len(pages)

        # The anchor is the position of (0, 0) relative to the top-left corner. It comes from the
        # sprite bounds, so it is the same for every frame.
        xmin, ymin, xmax, ymax = self.bounds
        orig_w = xmax - xmin
        orig_h = ymax - ymin
        anchor = {
            "x": -xmin / orig_w if orig_w > 0 else 0,
            "y": -ymin / orig_h if orig_h > 0 else 0,
        }

        result: list[Page] = []

        for page_idx, frame_indices in enumerate(pages):
            page_image, frames_data = self._render_page(Image, frame_indices, cols, margin, anchor)

            page_name = self.name if page_idx == 0 else f"{self.name}-{page_idx}"
            page_data: dict = {
                "frames": frames_data,
                "meta": {
                    "app": "noxine",
                    "image": f"{page_name}.webp",
                    "format": "RGBA8888",
                    "size": {"w": page_image.width, "h": page_image.height},
                    "scale": self.zoom,
                },
            }

            # Shared metadata lives only on the main page.
            if page_idx == 0:
                if n_pages > 1:
                    page_data["meta"]["related_multi_packs"] = [f"{self.name}-{k}.json" for k in range(1, n_pages)]

                page_data["flash_frames"] = self.flash_frames

                if self.animations:
                    page_data["animations"] = self.animations

            result.append(Page(page_name, page_image, page_data))

        return result

    def write(
        self,
        out_dir: Path | str,
        margin: int = 1,
        max_size: int = MAX_ATLAS_SIZE,
        quality: int = 90,
        lossless: bool = False,
    ) -> list[Path]:
        """Pack and write every page into `out_dir`. Returns every written path."""
        written: list[Path] = []

        for page in self.pack(margin, max_size):
            written.extend(page.write(out_dir, quality, lossless))

        return written

    def _render_page(self, image_module, frame_indices: list[int], cols: int, margin: int, anchor: dict):
        # Precise grid layout: each column is as wide as its widest frame, each row as tall as its
        # tallest frame.
        rows = math.ceil(len(frame_indices) / cols) if frame_indices else 1
        col_widths = [0] * cols
        row_heights = [0] * rows

        for local_i, gi in enumerate(frame_indices):
            image = self.frames[gi]
            col_widths[local_i % cols] = max(col_widths[local_i % cols], image.width + margin)
            row_heights[local_i // cols] = max(row_heights[local_i // cols], image.height + margin)

        page_image = image_module.new("RGBA", (sum(col_widths) or 1, sum(row_heights) or 1), (0, 0, 0, 0))
        frames_data = {}

        for local_i, gi in enumerate(frame_indices):
            col = local_i % cols
            row = local_i // cols
            x = sum(col_widths[:col])
            y = sum(row_heights[:row])

            image = self.frames[gi]
            page_image.paste(image, (x, y))

            frames_data[str(gi)] = {
                "frame": {"x": x, "y": y, "w": image.width, "h": image.height},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": image.width, "h": image.height},
                "sourceSize": {"w": image.width, "h": image.height},
                "anchor": anchor,
            }

        return page_image, frames_data
