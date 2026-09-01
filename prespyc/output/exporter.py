"""One-call export of a SWF character to a WEBP spritesheet."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import ScaleResizer
from prespyc.output.spritesheet import MAX_ATLAS_SIZE, Spritesheet

if TYPE_CHECKING:
    from prespyc.extractor.drawable import Drawable
    from prespyc.swf_file import SwfFile


def build_spritesheet(
    drawable: Drawable,
    name: str,
    zoom: float = 1.0,
    recursive: bool = True,
    rasterizer=None,
    subpixel_stroke_width: bool = True,
) -> Spritesheet:
    """
    Render every frame of `drawable` and collect them into a `Spritesheet`.

    `recursive` counts the frames of the children too, which is what an animation needs: a sprite
    whose own timeline has one frame can still animate through a nested sprite.
    """
    converter = Converter(
        resizer=ScaleResizer(zoom) if zoom != 1.0 else None,
        rasterizer=rasterizer,
        subpixel_stroke_width=subpixel_stroke_width,
    )

    frame_count = drawable.frames_count(recursive)
    frames = [converter.to_image(drawable, frame) for frame in range(frame_count)]

    bounds = drawable.bounds
    scale = zoom / 20

    return Spritesheet(
        name=name,
        frames=frames,
        bounds=(bounds.xmin * scale, bounds.ymin * scale, bounds.xmax * scale, bounds.ymax * scale),
        flash_frames=[{"frames": list(range(frame_count))}],
        zoom=zoom,
    )


def export(
    swf: SwfFile | Path | str,
    selector: int | str,
    out_dir: Path | str,
    zoom: float = 1.0,
    name: str | None = None,
    margin: int = 1,
    max_size: int = MAX_ATLAS_SIZE,
    quality: int = 90,
    lossless: bool = False,
) -> list[Path]:
    """
    Render a character to `out_dir` as `{name}.webp` + `{name}.json`, and return the written paths.

    `selector` is a character id or an exported name; `name` defaults to it. Frames that do not fit
    on one atlas page spill into `{name}-1`, `{name}-2`, … linked by `meta.related_multi_packs`.

    `flash_frames` is a flat frame list. Richer playback metadata (named animations, loop flags) is
    application specific and belongs to the caller.
    """
    from prespyc.swf_file import SwfFile as SwfFileType

    file = swf if isinstance(swf, SwfFileType) else SwfFileType(swf)
    drawable = file.extractor[selector]

    sheet = build_spritesheet(drawable, name if name is not None else str(selector), zoom)

    return sheet.write(out_dir, margin=margin, max_size=max_size, quality=quality, lossless=lossless)
