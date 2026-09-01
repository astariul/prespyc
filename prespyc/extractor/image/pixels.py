"""
Raster pixel buffers, standing in for PHP's GD extension.

ArakneSwf decodes every SWF bitmap through GD, whose alpha channel is 7 bit and inverted: 0 is
opaque and 127 fully transparent. Widening it back to PNG's 8 bit repeats the most significant bit
as the least significant one, so 0 maps to 255 and 127 to 0 — and an 8 bit alpha does *not* survive
the round trip (128 comes back as 129). That quantisation is baked into the golden images, so a
buffer keeps its alpha on GD's scale and only widens it when a PNG is written.

Alpha blending is not modelled: every call site of the original either disables it or writes opaque
colors, so `imagesetpixel()` never actually blends.

The per-pixel loops of `GD.php` are folded into whole-plane operations here — a lookup table per
channel plus `bytes.translate()`. The arithmetic is the same, byte for byte; only the Python-level
loop is gone.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any

from PIL import Image

if TYPE_CHECKING:
    from prespyc.parser.structure.record.color_transform import ColorTransform

ALPHA_OPAQUE = 0
"""GD alpha of a fully opaque pixel."""

ALPHA_TRANSPARENT = 127
"""GD alpha of a fully transparent pixel."""

_DEFAULT_JPEG_QUALITY = 75
"""libjpeg's own default, which GD keeps when it is asked for quality -1."""

_DEFAULT_PNG_COMPRESSION = 6
"""zlib's own default, which GD keeps when it is asked for compression -1."""

_PNG_ALPHA = bytes(255 - ((a << 1) + (a >> 6)) if a <= ALPHA_TRANSPARENT else 0 for a in range(256))
"""
GD alpha (0-127) to PNG alpha (0-255).

libgd repeats the most significant bit as the least significant one, so that 0 maps to 255 and 127
to 0. Entries above 127 are unreachable: a GD alpha never leaves that range.
"""

_GD_ALPHA = bytes(ALPHA_TRANSPARENT - (a >> 1) for a in range(256))
"""PNG or SWF alpha (0-255) to GD alpha (0-127)."""

_KEEP_OPAQUE = bytes(0 if a == ALPHA_TRANSPARENT else 255 for a in range(256))
"""GD alpha to a byte mask that is 0 on a fully transparent pixel and 255 everywhere else."""

_UNPREMULTIPLIED = bytes(
    0 if alpha == 0 else min(int(value * (255 / alpha)), 255) for alpha in range(256) for value in range(256)
)
"""
`[(alpha << 8) | value]` → the color component with its alpha divided out.

SWF stores 32 bit bitmaps and the JPEG alpha plane premultiplied by alpha, GD does not, so the
multiplication has to be undone. The float division and the truncating cast are PHP's:
`(int) ($value * (255 / $alpha))` differs from `intdiv($value * 255, $alpha)` on 75 of the 65536
pairs. An alpha of 0 carries no color at all, so the component is dropped.
"""


def fix_jpeg_data(image_data: bytes) -> bytes:
    """
    Strip the extra SOI/EOI markers and the invalid headers that SWF files add to JPEG data.

    The result is wrapped in exactly one SOI/EOI pair, which every decoder accepts.
    """
    length = len(image_data)
    fixed = bytearray()
    pos = 0

    # JPEG markers always start with 0xff, then a byte indicating the marker.
    # So find the next marker, and process it until the end of the data.
    while (next_pos := image_data.find(b"\xff", pos)) != -1 and next_pos < length - 1:
        marker = image_data[next_pos + 1]

        # Ignore SOI and EOI markers
        if marker == 0xD8 or marker == 0xD9:
            fixed += image_data[pos:next_pos]
            pos = next_pos + 2
            continue

        # Marker with length: do not change and skip the length
        if marker != 0 and (marker < 0xD0 or marker > 0xD7) and next_pos + 3 < length:
            size = (image_data[next_pos + 2] << 8) + image_data[next_pos + 3]
            fixed += image_data[pos : next_pos + size + 2]
            pos = next_pos + size + 2
        else:
            # Marker without length: simply copy it and continue
            fixed += image_data[pos : next_pos + 2]
            pos = next_pos + 2

    # Add the valid header and footer
    return b"\xff\xd8" + bytes(fixed) + b"\xff\xd9"


def image_size(data: bytes) -> tuple[int, int] | None:
    """
    Pixel size of an encoded image, or `None` when it cannot be decoded.

    PHP `getimagesizefromstring()`, which returns `false` on invalid data.
    """
    try:
        with Image.open(io.BytesIO(data)) as image:
            return image.size
    except Exception:
        # Any decoder failure means "not an image", which is PHP returning false.
        return None


class Pixels:
    """
    A raster buffer with GD's pixel model.

    Two flavours, as in GD: a true color buffer holding four 8 bit planes (alpha on GD's inverted
    0-127 scale), and a palette buffer holding one color table index per pixel. Build one with
    `create()`, `with_palette()`, `from_png()` or `from_jpeg()`.
    """

    __slots__ = (
        "_alpha",
        "_blue",
        "_green",
        "_indices",
        "_palette_alpha",
        "_palette_rgb",
        "_red",
        "height",
        "width",
    )

    def __init__(self, width: int, height: int, palette: bool) -> None:
        self.width = width
        self.height = height

        count = width * height

        self._indices: bytearray | None = bytearray(count) if palette else None
        self._palette_rgb = bytearray()
        self._palette_alpha = bytearray()

        self._red = bytearray(count)
        self._green = bytearray(count)
        self._blue = bytearray(count)
        self._alpha = bytearray(count)  # 0 is opaque, so a fresh true color buffer is opaque black

    # ------------------------------------------------------------------------------------ building

    @classmethod
    def create(cls, width: int, height: int) -> Pixels:
        """PHP `imagecreatetruecolor()`: a true color buffer filled with opaque black."""
        return cls(width, height, False)

    @classmethod
    def with_palette(cls, width: int, height: int) -> Pixels:
        """PHP `imagecreate()`: a palette buffer, every pixel on the first color table entry."""
        return cls(width, height, True)

    @classmethod
    def from_jpeg(cls, jpeg_data: bytes) -> Pixels:
        """Decode JPEG data, fixing its extra SWF markers first."""
        return cls._decode(fix_jpeg_data(jpeg_data), "Invalid JPEG data")

    @classmethod
    def from_png(cls, image_data: bytes) -> Pixels:
        """Decode PNG data."""
        return cls._decode(image_data, "Invalid PNG data")

    @classmethod
    def _decode(cls, data: bytes, message: str) -> Pixels:
        try:
            with Image.open(io.BytesIO(data)) as image:
                has_alpha = image.has_transparency_data
                source = image.convert("RGBA" if has_alpha else "RGB")
        except Exception as error:
            raise ValueError(f"{message}: {error}") from error

        pixels = cls.create(source.width, source.height)
        raw = source.tobytes()
        step = 4 if has_alpha else 3

        pixels._red = bytearray(raw[0::step])
        pixels._green = bytearray(raw[1::step])
        pixels._blue = bytearray(raw[2::step])

        if has_alpha:
            pixels._alpha = bytearray(raw[3::step].translate(_GD_ALPHA))

        return pixels

    # ------------------------------------------------------------------------------------- palette

    def allocate_color(self, red: int, green: int, blue: int) -> int:
        """PHP `imagecolorallocate()`: append an opaque color to the table and return its index."""
        return self.allocate_color_alpha(red, green, blue, ALPHA_OPAQUE)

    def allocate_color_alpha(self, red: int, green: int, blue: int, alpha: int) -> int:
        """PHP `imagecolorallocatealpha()`; `alpha` is on GD's inverted 0-127 scale."""
        assert self._indices is not None, "only a palette buffer has a color table"

        index = len(self._palette_alpha)
        self._palette_rgb += bytes((red, green, blue))
        self._palette_alpha.append(alpha)

        return index

    def write_indices(self, indices: bytes | bytearray) -> None:
        """Replace every pixel with a color table index, in row order."""
        assert self._indices is not None, "only a palette buffer is indexed"
        assert len(indices) == self.width * self.height, "one index per pixel"

        self._indices = bytearray(indices)

    # ---------------------------------------------------------------------------------- true color

    def write_xrgb(self, data: bytes) -> None:
        """
        Fill the color planes from 4 bytes per pixel, the first ignored.

        That is the layout of a 24 bit SWF lossless bitmap, whose pixels are 32 bit aligned. The
        alpha plane is left untouched, so the buffer stays opaque.
        """
        end = self.width * self.height * 4

        self._red = bytearray(data[1:end:4])
        self._green = bytearray(data[2:end:4])
        self._blue = bytearray(data[3:end:4])

    def write_premultiplied_argb(self, data: bytes) -> None:
        """
        Fill every plane from 4 premultiplied bytes per pixel: alpha, red, green, blue.

        That is the layout of a 32 bit SWF lossless bitmap. A pixel with an alpha of 0 becomes
        transparent black: its color cannot be recovered.
        """
        end = self.width * self.height * 4
        alpha = data[0:end:4]

        self._red = _unpremultiply(alpha, data[1:end:4])
        self._green = _unpremultiply(alpha, data[2:end:4])
        self._blue = _unpremultiply(alpha, data[3:end:4])
        self._alpha = bytearray(alpha.translate(_GD_ALPHA))

    def apply_alpha_plane(self, alpha_data: bytes) -> None:
        """
        Apply a separate alpha plane, one byte per pixel, to an opaque true color buffer.

        The color planes are premultiplied by that alpha, so the multiplication is undone. Used for
        the alpha channel a `DefineBitsJPEG3`/`DefineBitsJPEG4` tag stores beside its JPEG data.
        """
        alpha = alpha_data[: self.width * self.height]

        self._red = _unpremultiply(alpha, self._red)
        self._green = _unpremultiply(alpha, self._green)
        self._blue = _unpremultiply(alpha, self._blue)
        self._alpha = bytearray(alpha.translate(_GD_ALPHA))

    # ------------------------------------------------------------------------------------ transform

    def transform_colors(self, matrix: ColorTransform) -> None:
        """Apply the color transform matrix to each pixel of the image, in place."""
        self._to_true_color()

        red = self._red.translate(_channel_table(matrix.red_mult, matrix.red_add))
        green = self._green.translate(_channel_table(matrix.green_mult, matrix.green_add))
        blue = self._blue.translate(_channel_table(matrix.blue_mult, matrix.blue_add))
        alpha = self._alpha

        if ALPHA_TRANSPARENT in alpha:
            # Flash does not apply a color transform on a transparent pixel, it stays transparent
            # black — GD's 0x7F000000.
            keep = alpha.translate(_KEEP_OPAQUE)
            red = _masked(red, keep)
            green = _masked(green, keep)
            blue = _masked(blue, keep)

        self._red = red
        self._green = green
        self._blue = blue
        self._alpha = alpha.translate(_alpha_table(matrix.alpha_mult, matrix.alpha_add))

    def _to_true_color(self) -> None:
        """PHP `imagepalettetotruecolor()`: expand a palette buffer, or do nothing."""
        indices = self._indices

        if indices is None:
            return

        rgb = self._palette_rgb

        self._red = indices.translate(_palette_table(rgb[0::3]))
        self._green = indices.translate(_palette_table(rgb[1::3]))
        self._blue = indices.translate(_palette_table(rgb[2::3]))
        self._alpha = indices.translate(_palette_table(self._palette_alpha))

        self._indices = None
        self._palette_rgb = bytearray()
        self._palette_alpha = bytearray()

    # -------------------------------------------------------------------------------------- export

    def to_png(self, compression: int = -1) -> bytes:
        """Render the image as a PNG. `compression` goes from 0 to 9, -1 for the default."""
        image, options = self._to_png_image()
        buffer = io.BytesIO()

        image.save(
            buffer,
            "PNG",
            compress_level=_DEFAULT_PNG_COMPRESSION if compression < 0 else compression,
            **options,
        )

        return buffer.getvalue()

    def to_jpeg(self, quality: int = -1) -> bytes:
        """
        Render the image as a JPEG, losing the alpha channel.

        `quality` goes from 0 (worst) to 100 (best), -1 for the default.
        """
        buffer = io.BytesIO()

        self._to_rgb_image().save(
            buffer,
            "JPEG",
            quality=_DEFAULT_JPEG_QUALITY if quality < 0 else quality,
        )

        return buffer.getvalue()

    def _to_png_image(self) -> tuple[Image.Image, dict[str, Any]]:
        indices = self._indices

        if indices is not None:
            image = Image.frombytes("P", (self.width, self.height), bytes(indices))
            image.putpalette(bytes(self._palette_rgb))
            alpha = bytes(self._palette_alpha).translate(_PNG_ALPHA)

            # GD only writes a tRNS chunk when the color table holds a non-opaque entry.
            if alpha.count(255) == len(alpha):
                return image, {}

            return image, {"transparency": alpha}

        size = (self.width, self.height)
        planes = (
            Image.frombytes("L", size, bytes(self._red)),
            Image.frombytes("L", size, bytes(self._green)),
            Image.frombytes("L", size, bytes(self._blue)),
            Image.frombytes("L", size, bytes(self._alpha.translate(_PNG_ALPHA))),
        )

        return Image.merge("RGBA", planes), {}

    def _to_rgb_image(self) -> Image.Image:
        size = (self.width, self.height)
        indices = self._indices

        if indices is not None:
            image = Image.frombytes("P", size, bytes(indices))
            image.putpalette(bytes(self._palette_rgb))

            return image.convert("RGB")

        planes = (
            Image.frombytes("L", size, bytes(self._red)),
            Image.frombytes("L", size, bytes(self._green)),
            Image.frombytes("L", size, bytes(self._blue)),
        )

        return Image.merge("RGB", planes)


def _unpremultiply(alpha: bytes | bytearray, values: bytes | bytearray) -> bytearray:
    """Divide a color plane by its alpha plane, the way `GD::setPixelAlpha()` does."""
    table = _UNPREMULTIPLIED

    return bytearray(table[(a << 8) | v] for a, v in zip(alpha, values))


def _masked(values: bytearray, keep: bytearray) -> bytearray:
    """`values` with every byte zeroed where `keep` is zero."""
    size = len(values)

    return bytearray((int.from_bytes(values, "big") & int.from_bytes(keep, "big")).to_bytes(size, "big"))


def _clamp(value: int) -> int:
    # Do not use min and max: the original avoids them for performance reasons.
    if value > 255:
        return 255

    return 0 if value < 0 else value


def _channel_table(mult: int, add: int) -> bytes:
    """Color transform of one color channel, as a 256 entry lookup table."""
    return bytes(_clamp(((value * mult) >> 8) + add) for value in range(256))


def _alpha_table(mult: int, add: int) -> bytes:
    """
    Color transform of the alpha channel, as a 256 entry lookup table on GD alpha.

    A GD alpha of 127 means the pixel is fully transparent, and Flash leaves those alone.
    """
    table = bytearray(256)

    for gd_alpha in range(ALPHA_TRANSPARENT + 1):
        flash_alpha = (ALPHA_TRANSPARENT - gd_alpha) << 1  # Convert to flash alpha (0-255)

        if flash_alpha == 0:
            table[gd_alpha] = ALPHA_TRANSPARENT
            continue

        # Convert back to GD alpha (0-127)
        table[gd_alpha] = ALPHA_TRANSPARENT - (_clamp(((flash_alpha * mult) >> 8) + add) >> 1)

    return bytes(table)


def _palette_table(entries: bytearray) -> bytes:
    """One component of a color table, padded to the 256 entries `bytes.translate()` wants."""
    return bytes(entries[:256]).ljust(256, b"\x00")
