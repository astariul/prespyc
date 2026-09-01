# prespyc

SWF parsing and resource extraction, in pure Python.

`prespyc` reads Adobe Flash `.swf` files and turns their assets into **WEBP spritesheets with
PixiJS-compatible JSON** — no Java, no ImageMagick, no external binary. It is a Python port of
[ArakneSwf](https://github.com/Arakne/ArakneSwf), and exists to replace
[ffdec](https://github.com/jindrapetrik/jpexs-decompiler) in
[noxine](https://github.com/astariul/noxine)'s asset pipeline.

## Status

Under construction. See [PLAN.md](PLAN.md) for the porting plan and
[CONVENTIONS.md](CONVENTIONS.md) for the PHP → Python rules.

## Install

```sh
uv add prespyc
```

## Use

```python
import prespyc

swf = prespyc.open("1047.swf")

variables = swf.variables  # ActionScript 2 variables
sprite = swf.extractor["anim0R"]  # by exported name, or by character id
svg = sprite.to_svg(frame=0)
frames = sprite.frames_count(True)  # counting the children, i.e. what actually animates

# writes export/anim0R.webp + export/anim0R.json (+ anim0R-1.* when one page is not enough)
prespyc.export("1047.swf", "anim0R", "export/", zoom=2)
```

Rendering one frame, with control over the size:

```python
from prespyc.extractor.drawer.converter import Converter
from prespyc.extractor.drawer.resizer import FitSizeResizer

webp = Converter(FitSizeResizer(128, 128)).to_webp(sprite, frame=5, lossless=True)
```

Replacing noxine's ffdec calls, keeping ffdec's on-disk layout:

```python
from prespyc.output.ffdec_compat import ffdec_export

ffdec_export("sprite", "1047.swf", "out/", chids=[62])  # out/DefineSprite_62_anim0R/1.png ...
```

## License

LGPL-3.0-or-later, as ArakneSwf.
