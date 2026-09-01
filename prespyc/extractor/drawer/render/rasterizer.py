"""SVG rasterizer backends."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from PIL import Image


@runtime_checkable
class SvgRasterizer(Protocol):
    """
    Turns an SVG document into pixels.

    The SVG carries its own `width`/`height`, so the backend only has to honour them.
    """

    def rasterize(self, svg: str, background: str | None = None) -> Image.Image:
        """
        Render `svg` to an RGBA image.

        `background` is a CSS color, or `None` for a transparent canvas.
        """
        ...


def default_rasterizer() -> SvgRasterizer:
    """
    The best rasterizer available.

    resvg first — it is the closest to what ArakneSwf recommends (librsvg-class engines) and handles
    SVG filters, gradients and clip paths well. cairosvg is the fallback when resvg is missing.
    """
    from prespyc.extractor.drawer.render.resvg import ResvgRasterizer

    if ResvgRasterizer.available():
        return ResvgRasterizer()

    from prespyc.extractor.drawer.render.cairo import CairoRasterizer

    if CairoRasterizer.available():
        return CairoRasterizer()

    raise RuntimeError("No SVG rasterizer available: install `resvg-py` (preferred) or `cairosvg`")
