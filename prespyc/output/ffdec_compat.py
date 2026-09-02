"""
Compatibility shim for pipelines built around ffdec (JPEXS Free Flash Decompiler).

`ffdec_export()` mirrors the arguments and the on-disk layout of ffdec's `-export` command, so a
caller can swap the import and drop the Java dependency without changing anything else. Frames are
written as PNG, because that is what ffdec wrote.

This exists for migration only. The native path is `prespyc.export()`, which writes WEBP and its
JSON directly.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import ScaleResizer
from prespyc.swf_file import SwfFile

if TYPE_CHECKING:
    from prespyc.extractor.drawable import Drawable

ZOOM = 2
"""Render scale of the shim, matching the `-zoom 2` that ffdec pipelines typically passed."""


def ffdec_export(
    export_type: str,
    in_swf: Path | str,
    out_folder: Path | str,
    clean_folder: bool = True,
    chids: list[int] | None = None,
    frame_idx: int | None = None,
    subframes: int | None = None,
) -> None:
    """
    Export characters of `in_swf` under `out_folder`, in ffdec's layout.

    `export_type` accepts `"sprite"` and `"shape"`. Each character goes to
    `{out_folder}/DefineSprite_{id}_{exported name}/{frame + 1}.png` (the name part is omitted when
    the character is not exported), which is the layout ffdec produces.

    `chids` restricts the export to those character ids. `frame_idx` renders one frame only, and
    `subframes` splits that frame into that many sub-steps, as ffdec's `-sublength` does.

    `export_type="script"` is **not** supported: it produced decompiled ActionScript, which
    `prespyc` does not do. Read the values directly instead — `SwfFile.variables` runs the
    `DoAction` tags and returns the resulting globals.
    """
    if export_type == "script":
        raise NotImplementedError(
            "prespyc does not decompile ActionScript. Use SwfFile.variables to read the values "
            "the DoAction tags assign."
        )

    if export_type not in ("sprite", "shape"):
        raise ValueError(f"Unsupported export type: {export_type}")

    out = Path(out_folder)

    if clean_folder:
        shutil.rmtree(out, ignore_errors=True)

    file = SwfFile(in_swf)
    extractor = file.extractor
    names = {id: name for name, id in extractor.exported.items()}

    if chids:
        targets = {id: extractor.character(id) for id in chids}
    elif export_type == "shape":
        targets = dict(extractor.shapes)
    else:
        targets = dict(extractor.sprites)

    converter = Converter(resizer=ScaleResizer(ZOOM))

    for character_id, drawable in targets.items():
        prefix = "DefineShape" if export_type == "shape" else "DefineSprite"
        name = names.get(character_id)
        directory = out / (f"{prefix}_{character_id}_{name}" if name else f"{prefix}_{character_id}")
        directory.mkdir(parents=True, exist_ok=True)

        for index, frame in enumerate(_frames(drawable, frame_idx, subframes)):
            converter.to_image(drawable, frame).save(directory / f"{index + 1}.png", format="PNG")


def _frames(drawable: Drawable, frame_idx: int | None, subframes: int | None) -> list[int]:
    if frame_idx is None:
        return list(range(drawable.frames_count(True)))

    if not subframes or subframes <= 1:
        return [frame_idx]

    # ffdec's -sublength splits one frame into several steps. Without sub-frame interpolation the
    # honest equivalent is to repeat the frame, so the frame count the caller expects still matches.
    return [frame_idx] * subframes
