"""Rendering a drawable to SVG or WEBP."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc._util import num
from prespyc.extractor.drawer.svg.svg_canvas import SvgCanvas

if TYPE_CHECKING:
    from PIL import Image

    from prespyc.extractor.drawable import Drawable
    from prespyc.extractor.drawer.render.rasterizer import SvgRasterizer
    from prespyc.extractor.drawer.resizer import ImageResizer


class Converter:
    """
    Renders a drawable.

    SVG is the engine: WEBP goes through the SVG and a rasterizer. ArakneSwf offers PNG, GIF, JPEG
    and animated output too; `prespyc` keeps only WEBP, which is what the PixiJS spritesheets need.
    """

    __slots__ = ("background_color", "rasterizer", "resizer", "subpixel_stroke_width")

    def __init__(
        self,
        resizer: ImageResizer | None = None,
        background_color: str | None = None,
        rasterizer: SvgRasterizer | None = None,
        subpixel_stroke_width: bool = True,
    ) -> None:
        self.resizer = resizer
        """Output size. `None` keeps the drawable's own size."""

        self.background_color = background_color
        """CSS background color, or `None` for a transparent canvas."""

        self.rasterizer = rasterizer
        """SVG rasterizer. `None` picks the best available backend on first use."""

        self.subpixel_stroke_width = subpixel_stroke_width
        """See `SvgBuilder.subpixel_stroke_width`."""

    def to_svg(self, drawable: Drawable, frame: int = 0) -> str:
        """Render to SVG, applying the resizer when there is one."""
        bounds = drawable.bounds
        canvas = SvgCanvas(bounds, self.subpixel_stroke_width)
        drawable.draw(canvas, frame)

        if self.resizer is None:
            return canvas.render()

        width = bounds.width / 20
        height = bounds.height / 20
        new_width, new_height = self.resizer.scale(width, height)

        # Resizing keeps the drawing untouched and only restates the output size, so the viewBox has
        # to carry the original size.
        canvas.root.set_attribute("width", num(new_width))
        canvas.root.set_attribute("height", num(new_height))
        canvas.root.set_attribute("viewBox", f"0 0 {num(width)} {num(height)}")

        return canvas.render()

    def to_image(self, drawable: Drawable, frame: int = 0) -> Image.Image:
        """Render to an RGBA image."""
        if self.rasterizer is None:
            from prespyc.extractor.drawer.render.rasterizer import default_rasterizer

            self.rasterizer = default_rasterizer()

        return self.rasterizer.rasterize(self.to_svg(drawable, frame), self.background_color)

    def to_webp(self, drawable: Drawable, frame: int = 0, quality: int = 90, lossless: bool = False) -> bytes:
        """Render to a WEBP blob."""
        import io

        image = self.to_image(drawable, frame)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=quality, lossless=lossless, method=6)

        return buffer.getvalue()
