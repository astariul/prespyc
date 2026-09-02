---
name: prespyc
description: Exports SWF sprites to WEBP spritesheets with PixiJS-compatible JSON, using the prespyc Python package. Use when extracting sprites, shapes, raster images or ActionScript variables out of .swf files, when replacing ffdec/JPEXS in an asset pipeline, and when one sprite needs a customized export — freezing a frame, slicing/repeating/reordering frames, composing frames from several characters, recolouring, or attaching a child.
when_to_use: Triggers on ".swf", "swf", "flash asset", "sprite extraction", "spritesheet", "texture atlas", "gfx export", "ffdec", "JPEXS", "prespyc", or on any request to turn Flash assets into something a web client can draw.
---

# Export SWF sprites with prespyc

`prespyc` is a pure-Python SWF reader and resource extractor — a port of
[ArakneSwf](https://github.com/Arakne/ArakneSwf). It parses `.swf`, renders characters through an
SVG engine, rasterizes with [resvg](https://github.com/linebender/resvg), and writes **WEBP atlas
pages plus PixiJS JSON**. No Java, no ImageMagick, no subprocess.

It replaces `ffdec`/JPEXS. It is **read-only**: it never writes a SWF file, so customizing a sprite
means editing the parsed structures in memory before rendering (see *Customizing one sprite*).

## Install

```sh
uv add prespyc          # or: pip install prespyc
```

Needs Python >= 3.13. Pulls `pillow`, `resvg-py` and `xxhash`. `cairosvg` is an optional fallback
rasterizer, only needed where `resvg-py` has no wheel.

## Mental model

```
SwfFile → Extractor → drawable (sprite / shape / morph shape / image / timeline)
        → Converter (SVG → resvg → RGBA)
        → Spritesheet (atlas pages + JSON)
```

Six facts that prevent most mistakes:

1. **Coordinates are in twips**, 1/20th of a pixel. `bounds` is a `Rectangle(xmin, xmax, ymin, ymax)`
   with `.width` / `.height` properties — divide by 20 for pixels, then multiply by the zoom.
2. **`frames_count(recursive=True)` is the number that matters.** A sprite whose own timeline has one
   frame still animates through a nested sprite. Always export `range(drawable.frames_count(True))`.
3. **Everything returns a new instance.** `transform_colors()`, `modify()`, `with_*()`,
   `keep_frame_by_*()` never mutate. Rebind the result.
4. **`bounds`, `timeline`, `shape`, `exported`, `shapes`, `sprites`, `images` are properties**, not
   methods. `frames_count()`, `to_svg()`, `character()`, `timeline(bool)` on the extractor are methods.
5. **Strings out of the parser are `bytes`** (a frame label, a `PlaceObject` name). Decode with
   `prespyc._util.decode_swf_text(raw, swf.header.version)`.
6. **The extractor caches** every character it processes. Call `extractor.release()` between files in
   a batch, or memory grows with the whole corpus.

## Export a sprite

The one-call path covers most needs:

```python
import prespyc

# writes out/anim0R.webp + out/anim0R.json
paths = prespyc.export("1047.swf", "anim0R", "out/", zoom=2)
```

`export(swf, selector, out_dir, zoom=1.0, name=None, margin=1, max_size=8192, quality=90, lossless=False)`

- `swf` — a path or an already-open `SwfFile`.
- `selector` — an exported name (`str`) or a character id (`int`).
- `name` — output base name; defaults to `str(selector)`.
- `max_size` — page limit in pixels. Frames that do not fit spill into `{name}-1`, `{name}-2`, …,
  linked from `meta.related_multi_packs` on the main page. Frame indices stay global across pages.

The JSON is noxine's schema, so PixiJS consumes it directly:

```jsonc
{
  "frames": { "0": { "frame": {"x":0,"y":0,"w":40,"h":42}, "rotated": false, "trimmed": false,
                     "spriteSourceSize": {...}, "sourceSize": {...},
                     "anchor": {"x":0.42,"y":0.91} } },
  "meta": { "app": "noxine", "image": "anim0R.webp", "format": "RGBA8888",
            "size": {"w":..,"h":..}, "scale": 2, "related_multi_packs": ["anim0R-1.json"] },
  "flash_frames": [{"frames": [0, 1, 2]}],
  "animations": {}
}
```

`anchor` is where the SWF origin sits inside the frame, as a fraction of its size — the same for
every frame, derived from the sprite bounds.

## Inspect a SWF

```python
swf = prespyc.open("1047.swf")

swf.valid()                  # header-only sanity check, no full parse
swf.header.version           # 7
swf.frame_rate               # 20, clamped to 1..120
swf.display_bounds           # Rectangle, in twips
swf.variables                # ActionScript 2 globals, from the DoAction tags

ex = swf.extractor
ex.exported                  # {"anim0R": 62, "staticR": 66, ...} name -> character id
ex.sprites                   # {id: SpriteDefinition}
ex.shapes, ex.morph_shapes, ex.images
ex["anim0R"]                 # by name
ex[62]                       # by character id; a MissingCharacter if absent
ex.timeline()                # the root timeline; timeline(False) to use frame bounds, not file bounds
```

Raster characters expose their own bytes: `image.to_png()`, `image.to_jpeg(quality=90)`,
`image.to_base64_data()`.

For a corrupt or sloppily authored file, relax the error flags:

```python
from prespyc.errors import Errors

swf = prespyc.open("corrupted.swf", errors=Errors.NONE)          # fail-safe: parse what you can
swf = prespyc.open("x.swf", errors=Errors.IGNORE_INVALID_TAG)    # strict, but skip bad tags
```

## Control the rendering

```python
from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import FitSizeResizer, ScaleResizer

sprite = swf.extractor["anim0R"]

Converter().to_svg(sprite, frame=3)                        # str
Converter(ScaleResizer(2.0)).to_image(sprite, frame=3)     # PIL.Image, RGBA
Converter(FitSizeResizer(128, 128)).to_webp(sprite, frame=3, lossless=True)   # bytes
```

`Converter(resizer=None, background_color=None, rasterizer=None, subpixel_stroke_width=True)`

- `background_color` — a CSS colour; `None` keeps the canvas transparent.
- `subpixel_stroke_width=False` — clamps strokes to a 1px minimum and marks them
  `non-scaling-stroke`. This is closer to how Flash drew thin lines at native size, at the cost of
  correct stroke width when rescaled. Use it when hairlines come out faint.

## Customizing one sprite

This is what `prespyc` is for inside a pipeline that used to patch SWF XML with ffdec. There is no
round-trip: get the `Timeline`, build the variant you want, render that. All of the operations below
are verified.

`Timeline(bounds, *frames)`, `timeline.frames` is a tuple of `Frame`, and each `Frame` holds
`objects: dict[int, FrameObject]` keyed by depth, in draw order.

**Work on the timeline that actually holds the frames.** An exported sprite is usually a one-frame
wrapper around the animating child, so slicing its own `timeline` does nothing useful. Address the
child by character id (`swf.extractor[61]`), the way ffdec-era code named the inner chid, or walk to
it:

```python
outer = swf.extractor["anim0R"]                       # 1 frame of its own, 40 recursively
inner = next(iter(outer.timeline.frames[0].objects.values())).object   # the child that animates
```

Then slice, repeat and reorder it — every result is a drawable:

```python
from prespyc.extractor.timeline.timeline import Timeline

tl = swf.extractor[61].timeline                                      # 40 frames

first_ten = Timeline(tl.bounds, *tl.frames[:10])                     # keep the first N
without_last = Timeline(tl.bounds, *tl.frames[:-3])                  # drop the last N
tripled = Timeline(tl.bounds, *(tl.frames * 3))                      # repeat the loop
padded = Timeline(tl.bounds, *tl.frames, *([tl.frames[-1]] * 5))     # pad by holding the last frame
labelled = tl.keep_frame_by_label("start")                           # single frame, by label
```

A `Timeline` must keep at least one frame — slicing to empty raises `AssertionError`. Use
`Timeline.empty()` for a deliberate blank.

**Freezing a sprite.** `keep_frame_by_number(n)` only collapses the timeline it is called on — a
nested child keeps animating, so `frames_count(True)` stays high. To freeze the whole tree, use the
modifier, which recurses:

```python
from prespyc.extractor.modifier.goto_and_stop import GotoAndStop

sprite.timeline.keep_frame_by_number(0).frames_count(True)   # 40 — the child still animates
sprite.modify(GotoAndStop(0)).frames_count(True)             # 1  — frozen
sprite.modify(GotoAndStop("stand"))                          # a label works too
```

**Composing frames out of different characters** — the equivalent of building a sprite whose frame 0
is one child, frame 1 another:

```python
from prespyc.extractor.timeline.frame import Frame
from prespyc.extractor.timeline.frame_object import FrameObject
from prespyc.parser.structure.record.matrix import Matrix

full = swf.extractor[202].modify(GotoAndStop(0))
empty = swf.extractor[202].modify(GotoAndStop(30))

bounds = full.bounds.union(empty.bounds)
sequence = [full, empty, full]

composed = Timeline(
    bounds,
    *(
        Frame(bounds, {0: FrameObject(depth=0, object=d, bounds=d.bounds, matrix=Matrix())})
        for d in sequence
    ),
)
```

**Moving, tinting or swapping a placed object.** `FrameObject.with_()` replaces only what you pass:

```python
from prespyc.parser.structure.record.color_transform import ColorTransform

frame = tl.frames[0]
obj = frame.objects[3]                                   # by depth, or frame.object_by_name("head")

moved = obj.with_(matrix=Matrix(translate_x=200, translate_y=-40))
swapped = obj.with_(object=swf.extractor[119])
tinted = obj.with_(color_transform=ColorTransform(red_mult=128, green_mult=128, blue_mult=128))

patched = Frame(frame.bounds, {**frame.objects, 3: moved}, frame.actions, frame.label)

```

**Recolouring a whole character**, recursively — cheaper and simpler than touching objects:

```python
darker = sprite.transform_colors(ColorTransform(red_mult=128, green_mult=128, blue_mult=128))
```

**Attaching a child** at a depth, e.g. an item in a character's hand:

```python
combined = sprite.with_attachment(swf.extractor["weapon"], depth=500, name="weapon")
```

**A custom modifier**, when a rule has to apply through the whole tree. Subclass
`BaseCharacterModifier` (every method is a no-op by default) and override what you need:

```python
from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier

class StripFilters(BaseCharacterModifier):
    """Drops every SWF filter, at every depth, at every level."""

    def apply_on_frame(self, frame):
        objects = {d: o.with_(filters=[]) for d, o in frame.objects.items()}
        return Frame(frame.bounds, objects, frame.actions, frame.label)

clean = sprite.modify(StripFilters())
```

Any `Timeline`, `Frame`-built variant or modified sprite is a drawable, so it goes straight into the
`Converter` or into `build_spritesheet`.

## Custom playback metadata

`prespyc.export()` writes a flat `flash_frames`. When the client needs named animations or a loop
flag, build the sheet and set them before writing:

```python
from prespyc.output.exporter import build_spritesheet

sheet = build_spritesheet(composed, "7519", zoom=2)      # renders every frame
n = len(sheet.frames)

sheet.animations = {"0": list(range(n))}
sheet.flash_frames = [{"animations": ["0"], "loop": True}]

sheet.write("out/", quality=90)
```

`Spritesheet(name, frames, bounds, flash_frames, animations, zoom)` — `frames` is a list of
`PIL.Image`, `bounds` is `(xmin, ymin, xmax, ymax)` in **output pixels** (twips / 20 * zoom) and
drives the anchor. `pack(margin, max_size)` returns `Page(name, image, data)` objects if you want the
images and JSON without writing them.

## Replacing ffdec

For a pipeline still reading ffdec's on-disk layout, the shim writes the same tree
(`{out}/DefineSprite_{id}_{name}/{frame + 1}.png`, PNG, `ZOOM = 2`):

```python
from prespyc.output.ffdec_compat import ZOOM, ffdec_export

ffdec_export("sprite", "1047.swf", "out/", chids=[62])
ffdec_export("sprite", "1047.swf", "out/", chids=[62], frame_idx=3, subframes=4)
```

`export_type="script"` **raises `NotImplementedError`**: `prespyc` does not decompile ActionScript.
Read the values instead — `swf.variables` runs the `DoAction` tags and returns the globals, which is
the same data the `.as` files were regex-scraped for.

## Batch pipelines

```python
for path in sorted(folder.glob("*.swf")):
    swf = prespyc.open(path, errors=Errors.NONE)
    for name, character_id in swf.extractor.exported.items():
        prespyc.export(swf, character_id, out / path.stem, name=name, zoom=2)
    swf.extractor.release()          # drop the caches before the next file
```

Rough cost for a 40-frame sprite at zoom 2: parse 0.04 s, SVG 0.24 s, full export ~4 s — the
rasterizing and WEBP encoding dominate, and both are native.

## Constraints

- **Never write a SWF.** There is no encoder. Build variants in memory, as above.
- **Do not mutate a drawable in place.** Use the returned instance.
- **Do not reimplement rendering.** If output looks wrong, check `subpixel_stroke_width`, the zoom,
  and whether you exported `frames_count(True)` frames.
- **Confirm before overwriting an output tree.** `ffdec_export(..., clean_folder=True)` deletes
  `out_folder` recursively; it defaults to `True`, matching ffdec.
- `Timeline(bounds)` with no frames raises `AssertionError`; keep at least one.
- `Opaque15Bit` lossless bitmaps and GIF-in-JPEG-tag payloads raise `NotImplementedError`, as in
  ArakneSwf. No fixture exercises either.
- Rendered pixels are equivalent to, not identical with, ffdec's or ArakneSwf's: a different SVG
  rasterizer draws antialiased edges slightly differently (measured ~0.2% visible difference).
