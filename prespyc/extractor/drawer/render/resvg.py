"""resvg rasterizer backend."""

from __future__ import annotations

import io

from PIL import Image


class ResvgRasterizer:
    """Rasterizes SVG with [resvg](https://github.com/linebender/resvg), through `resvg-py`."""

    __slots__ = ()

    @staticmethod
    def available() -> bool:
        try:
            import resvg_py  # noqa: F401
        except ImportError:
            return False

        return True

    def rasterize(self, svg: str, background: str | None = None) -> Image.Image:
        import resvg_py

        # resvg-py returns a PNG blob. `skip_system_fonts` keeps the output reproducible across
        # machines: SWF text is drawn as glyph outlines, so no font is needed.
        png = resvg_py.svg_to_bytes(svg_string=svg, background=background, skip_system_fonts=True)

        return Image.open(io.BytesIO(bytes(png))).convert("RGBA")
