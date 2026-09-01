"""cairosvg rasterizer backend, used when resvg is not installed."""

from __future__ import annotations

import io

from PIL import Image


class CairoRasterizer:
    """
    Rasterizes SVG with [cairosvg](https://cairosvg.org/).

    Fallback backend: it needs a system cairo, and its filter support is weaker than resvg's, so
    blurs and glows come out less faithful.
    """

    __slots__ = ()

    @staticmethod
    def available() -> bool:
        try:
            import cairosvg  # noqa: F401
        except ImportError:
            return False

        return True

    def rasterize(self, svg: str, background: str | None = None) -> Image.Image:
        import cairosvg

        png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), background_color=background)

        return Image.open(io.BytesIO(png)).convert("RGBA")
