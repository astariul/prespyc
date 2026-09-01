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
webp = sprite.to_webp(frame=0)

# writes export/anim0R.webp + export/anim0R.json
prespyc.export("1047.swf", "anim0R", out_dir="export/", zoom=2)
```

## License

LGPL-3.0-or-later, as ArakneSwf.
