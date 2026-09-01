# Porting Plan — ArakneSwf → Python (`prespyc`)

A plan to port [ArakneSwf](https://github.com/Arakne/ArakneSwf) (pure-PHP SWF parser + resource
extractor, ~20.7k LOC) into **`prespyc`** — a **standalone, pip-installable Python package**,
executed **entirely by agents**. `prespyc` is a *new* package that covers the same surface and
functionality as ArakneSwf but with an API redesigned to be **easy and idiomatic to use from
Python** — not a line-for-line transliteration. The end goal is to replace noxine's `ffdec` (JPEXS,
a flaky Java subprocess) with a native Python library that produces **JSON + WEBP** spritesheets
directly consumable by PixiJS.

---

## 1. Decisions (locked)

| Decision | Choice | Consequence |
|---|---|---|
| **Name / form** | Standalone package **`prespyc`** (own repo), noxine imports it | Clean test boundary; reuse ArakneSwf's own fixtures/goldens |
| **API design** | **New, Pythonic API** — *not* ArakneSwf-compatible | Rename classes/methods/attributes freely; optimize for Python ergonomics (properties, `__getitem__`, top-level helpers, dataclasses). Same *surface & behavior*, easier to use. No goal of API familiarity for ArakneSwf users. |
| **Scope** | **Full faithful port** of Parser + Extractor + AVM + SVG engine | Reuse the 59 SWF fixtures + ~1,130 golden SVGs as the acceptance oracle; low risk |
| **Output** | **One mode only: JSON + WEBP** atlas (noxine spritesheet format) | Drop PNG/GIF/JPEG/animated/raw-SVG *output*; keep the SVG *engine* internally |
| **Fidelity** | **Equivalent quality** (client may adjust) | Primary oracle = golden SVGs; raster/WEBP validated by spot-check vs current ffdec output |
| **Interface** | **Pure Python API**, no CLI | Do not port `src/Console/` (~720 LOC) |
| **ActionScript** | **Variable reading only** (like today's noxine scripts) | Port AVM's `variables()`/`execute()` faithfully (~710 LOC); no AS decompilation |
| **Rust** | Excluded | Pure Python; revisit only if profiling later demands it |

**Faithful behavior, Pythonic names.** The goldens constrain *output and behavior*, not identifiers.
So agents port the *algorithms and module structure* closely (to keep translation mechanical and the
golden oracle valid) but give everything idiomatic Python names and ergonomics from the start.

---

## 2. Why this is tractable

- **The hard 80% is self-validating.** ArakneSwf ships **59 SWF fixtures** and **~1,130 golden SVG
  files** (`tests/Extractor/Fixtures/…`), plus PHPUnit test classes mirroring every component. The
  parser + extractor + SVG builder are correct **iff** they reproduce those goldens. The goldens are
  SVG *output*, so renaming the API does not weaken them — agents port until the goldens match, a
  deterministic gate, not a judgment call.
- **WEBP is already a first-class path.** `Converter::toWebp()` exists in the PHP source; the render
  pipeline is **SVG → rasterizer → image blob**. We only swap the rasterizer backend
  (Imagick/rsvg → a Python SVG rasterizer) and keep the WEBP branch.
- **The parser is mechanical.** Binary reads map directly: PHP `unpack`/`pack` → Python `struct`,
  `inflate_*`/`gzuncompress` → `zlib`, `readonly` classes → frozen dataclasses.
- **The output format already exists in Python.** noxine's
  [scripts/spritesheet.py](../noxine/scripts/spritesheet.py) defines the exact PixiJS JSON schema
  (`frames`/`meta`/`flash_frames`/`animations`/`anchor`/`related_multi_packs`) and atlas packing —
  we port it to emit **WEBP** instead of PNG.

---

## 3. What ArakneSwf actually is (component map)

| PHP `src/` | LOC | Role | Port difficulty |
|---|---|---|---|
| `Parser/SwfReader.php` | 864 | Bit/byte primitive reader (most-depended-on file) | Mechanical, but exacting (bit alignment) |
| `Parser/Structure/**` | ~8.8k | 59 tag types, records, shape/morph records, actions | Voluminous, mechanical, parallelizable |
| `Avm/**` | 710 | AS2 bytecode interpreter → variables | Small, self-contained |
| `Extractor/Shape/**` | 1,511 | Parsed shape records → drawable paths + fill styles | Geometry; medium |
| `Extractor/MorphShape/**` | 769 | Morph-shape interpolation | Geometry; medium |
| `Extractor/Image/**` | 1,422 | JPEG/lossless/bits bitmap decode (`GD` → Pillow) | Fiddly pixel formats |
| `Extractor/Sprite/` + `Timeline/` + `Modifier/` | 1,602 | Display list, frames, gotoAndStop | Stateful; medium |
| `Extractor/SwfExtractor.php` | 422 | Entry: `shapes/sprites/timeline/character/byName/exported` | Orchestration |
| `Extractor/Drawer/DrawerInterface` + `Svg/**` | ~1,341 | Draw ops → **SVG** (validated by goldens) | Medium; the fidelity core |
| `Extractor/Drawer/Converter/**` | ~1,154 | SVG → raster (Imagick + rsvg/inkscape/native) → PNG/GIF/JPEG/**WEBP** | **Replace backend**, keep WEBP only |
| `Console/**` | 720 | CLI | **Dropped** |

---

## 4. Target package layout

Mirror ArakneSwf's module *structure* so translation stays mechanical and the golden tests remain
valid — but name everything Pythonically (the public API is new, not a PHP transliteration).

```
prespyc/
  pyproject.toml              # uv-managed (matches noxine tooling); deps: Pillow, resvg-py (or cairosvg), pytest
  prespyc/
    __init__.py               # Pythonic public API surface (§7)
    swf_file.py               # SwfFile
    errors.py                 # error flags + exception types
    _util.py
    parser/
      reader.py               # the bit/byte reader  (Phase 1)
      swf.py                  # tag iteration
      structure/
        record/               # rectangle, matrix, color, color_transform, gradients, filter/, shape/, morph_shape/
        tag/                  # 59 tag classes
        action/               # action records, opcodes, values
    avm/
      processor.py            # Phase 3
      state.py
      api/                    # script array/object
    extractor/
      extractor.py            # SwfExtractor equivalent
      shape/                  # Phase 4a
      morph_shape/            # Phase 4b
      image/                  # Phase 4c  (Pillow)
      sprite/  timeline/  modifier/   # Phase 4d
      drawer/
        drawer.py             # draw-ops protocol (was DrawerInterface)
        svg/                  # Phase 5: SVG builder, canvases, svg/filter/*
        render/               # Phase 6: SvgRasterizer backends (resvg / cairosvg)
        converter.py          # Phase 6: to_webp() only
    output/                   # NEW — the "one output type"
      spritesheet.py          # port of noxine spritesheet.py → WEBP pages + JSON
      exporter.py             # high-level: swf → {expid}.webp + {expid}.json
      ffdec_compat.py         # Phase 7: drop-in shim mirroring ffdec.py's signatures
  tests/
    fixtures/                 # copied verbatim from ArakneSwf/tests/**/Fixtures
    parser/  avm/  extractor/ …   # pytest translations of the PHPUnit suites
    conftest.py               # golden-SVG comparison harness + SWF builder helper
  CONVENTIONS.md              # PHP→Python idiom + naming policy (authored in Phase 0)
```

---

## 5. Rendering & output strategy

**Engine stays SVG-based** (that's what the goldens validate). Only the raster backend changes.

```
extractor → timeline/sprite/shape (a "drawable")
   → SVG builder (draw-ops protocol impl)        # Phase 5 — matches golden SVGs
   → SvgRasterizer backend  [resvg | cairosvg]   # Phase 6 — replaces Imagick/rsvg
   → RGBA bitmap → Pillow                          # Phase 6
   → WEBP page + spritesheet JSON                 # Phase 6 (output/)
```

- **Rasterizer**: default **resvg** (via `resvg-py`/CFFI or the `resvg` binary) — highest fidelity,
  handles SVG filters/gradients well; ArakneSwf itself warns Imagick's SVG support is poor and
  recommends rsvg/resvg-class engines. Fallback: **cairosvg** (pure-Python-friendly). Hide behind a
  `SvgRasterizer` protocol so it's swappable and the choice can be revisited without touching the
  engine.
- **WEBP encode + atlas packing**: Pillow. Reuse noxine's `plan_pages`/grid packer and the
  `MAX_ATLAS_SIZE`/`related_multi_packs` multi-page logic from
  [scripts/spritesheet.py](../noxine/scripts/spritesheet.py) verbatim, swapping `.png`→`.webp` and
  `format: "RGBA8888"`/`meta.image` accordingly.

**Output JSON schema** (unchanged from noxine, so PixiJS consumption is near-identical):
```jsonc
{
  "frames":   { "<i>": { "frame": {x,y,w,h}, "rotated": false, "trimmed": false,
                          "spriteSourceSize": {...}, "sourceSize": {...}, "anchor": {x,y} } },
  "meta":     { "app": "noxine", "image": "<name>.webp", "format": "RGBA8888",
                "size": {w,h}, "scale": <zoom>, "related_multi_packs?": [...] },
  "flash_frames": [...],       // timeline frame data (from Extractor Timeline)
  "animations":   { ... }      // named animations (optional)
}
```
`anchor` is derived from sprite bounds exactly as today; `flash_frames`/`animations` are built from
the ported timeline. (Fidelity target allows client-side tweaks if a field differs.)

---

## 6. Phased execution (agent-oriented)

Phases are **sequential acceptance gates**; work *within* Phases 2 and 4 **fans out** to parallel
agents. Every phase's Definition of Done is **green tests**, mostly translated from ArakneSwf's own
suite — no subjective sign-off.

### Phase 0 — Scaffold & test harness  *(1 agent, blocking)*
- Create repo, `pyproject.toml` (uv), package skeleton, pytest + CI.
- **Copy all fixtures** from `ArakneSwf/tests/**/Fixtures/` (59 SWF, ~1,130 golden SVGs, expected
  variables/JSON) into `tests/fixtures/`.
- Build the **golden harness** in `conftest.py`: given a fixture, run the port and compare SVG to
  the golden. Define SVG **normalization** (float precision, attribute order, whitespace) — decide
  once, apply everywhere. Port ArakneSwf's `SwfBuilder` test helper.
- Author **`CONVENTIONS.md`** — covers both idiom mapping and the **naming policy** (critical for
  parallel consistency): `unpack`→`struct`, `readonly` class→`@dataclass(frozen=True)`, PHP enum→
  `enum`, union return types→`typing.Union`, generators (`yield` in tag iteration), error-flag
  bitmask semantics (throw vs. fallback), 64-bit int assumptions, byte-string handling (`bytes`, not
  `str`); **naming**: `camelCase`→`snake_case`, getters→`@property`, `getX()/byName()/character()`→
  `x`/`by_name()`/`__getitem__`, top-level `open()`/`export()` helpers, no PHP-ism leakage.
- **Gate**: harness runs and reports N goldens as "not yet matched"; `pip install -e .` works.

### Phase 1 — Primitives + reader  *(1–2 agents, blocking)*
- `errors.py`, `_util.py`, core records (`Rectangle`, `Matrix`, `Color`, `ColorTransform`).
- `parser/reader.py` — the bit/byte reader; the linchpin.
- **Gate**: `tests/parser/test_reader.py` (from `SwfReaderTest.php`) green.

### Phase 2 — Parser structures, tags, actions  *(fan out: 4–6 agents)*
- **2a (records, first)**: `parser/structure/record/**` — shape records, morph records, gradients,
  filters. Everything else depends on these.
- **2b (parallel batches)**: 59 tag classes split by family (DefineShape\*, DefineSprite/PlaceObject\*,
  DefineBits\*/JPEG/Lossless, DefineMorphShape\*, DoAction/ExportAssets, Font/Text, control tags) +
  `parser/structure/action/**` + `parser/swf.py`.
- **Gate**: `test_swf.py`, `test_tag.py`, structure tests green; **all 59 fixtures parse without
  error** and tag counts/offsets match ArakneSwf's parser assertions.

### Phase 3 — AVM (variables)  *(1 agent; parallel with Phase 4)*
- `avm/**` + `swf_file.py` `execute()`/`variables()`. Function calls disabled by default (as upstream).
- **Gate**: `test_processor.py`, `test_script_array.py`, `test_script_object.py` green; `variables`
  matches expected values on the AVM fixtures.

### Phase 4 — Extractor engine  *(fan out after 2: 3–5 agents)*
- 4a `shape/` → 4b `morph_shape/` → 4c `image/` (Pillow: JPEG/lossless/bits decode) →
  4d `sprite/`+`timeline/`+`modifier/` → 4e `extractor.py`.
- (4a/4b/4c independent given records; 4d depends on 4a; 4e depends on all.)
- **Gate**: `Shape/MorphShape/Image/Sprite/Timeline/Extractor` test translations green.

### Phase 5 — SVG builder  *(2 agents)* — **primary fidelity gate**
- `drawer/drawer.py`, `drawer/svg/**` (SVG builder, canvases, `svg/filter/*` incl. blur).
- **Gate**: **all ~1,130 golden SVGs reproduced** (normalized comparison). When green, the whole
  parse→extract→SVG engine is proven faithful.

### Phase 6 — Rasterize → WEBP → JSON atlas  *(2 agents)* — the deliverable
- `drawer/render/` SvgRasterizer (resvg default, cairosvg fallback) behind a protocol.
- `drawer/converter.py`: port **`to_webp(drawable, frame, ...)`** + size/resizer logic
  (`FitSizeResizer`/`ScaleResizer`, `webp@128`-style specs). Drop all other formats.
- `output/spritesheet.py` (port of noxine's, WEBP) + `output/exporter.py`
  (`export(swf, selector, out_dir, zoom, max_size) → writes {expid}.webp + {expid}.json`).
- **Gate**: renders a set of real Dofus gfx SWFs; JSON validates against the noxine schema;
  **visual spot-check** vs current ffdec output within an agreed tolerance (image-diff script).

### Phase 7 — Public API + noxine seam  *(1 agent)*
- Finalize `prespyc/__init__.py` (§7).
- `output/ffdec_compat.py`: a shim mirroring [scripts/ffdec.py](../noxine/scripts/ffdec.py)'s
  `ffdec_export(export_type, in_swf, out_folder, chids, frame_idx, subframes)` and `ZOOM`, writing
  the same on-disk layout — so noxine can swap the import and delete the Java dependency with minimal
  churn.
- **Gate**: a noxine smoke test extracts one sprite through the shim end-to-end.

### Phase 8 — noxine migration  *(OUT OF SCOPE of the port; planned follow-on)*
Swap `prepare_sprite_extraction.py` / `extract_maps_spritesheets.py` / `spritesheet.py` to `prespyc`,
then tackle the big one: **`custom_exports.py`** currently uses ffdec's `swf2xml`/`xml2swf`
round-trip to patch specific sprites (see the ~40 `customize_xml_for_*` functions). **The port is
read-only** — it does not write SWF. These customizations must be **reimplemented as in-memory
manipulation** of parsed tags/timeline before rendering. This is a substantial, Dofus-specific
effort and is the single biggest migration risk — track it as its own project, and keep ffdec around
only for that step during transition if needed.

---

## 7. Public Python API (target — illustrative, names finalized during the port)

Designed for Python ergonomics: a top-level `open()`, properties instead of getters, `__getitem__`
lookup, methods on the drawable, and one-call helpers. (Not bound to ArakneSwf's names.)

```python
import prespyc

swf = prespyc.open("o2.swf")                # SwfFile
variables = swf.variables                   # property — AS2 variable reading (Phase 3)

ex = swf.extractor
sprite = ex["1964"]                         # by exported name or character id
timeline = ex.timeline
for name, asset in ex.exported.items():     # dict of exported assets
    ...

webp_bytes = sprite.to_webp(frame=0, quality=90)   # render straight off the drawable

# One-call export → writes export/1964.webp + export/1964.json (+ 1964-1.webp… multi-page)
prespyc.export("o2.swf", "1964", out_dir="export/", zoom=2)
```

---

## 8. Agent execution model

- **Golden-test-driven**: each agent's task = "port module X; make its translated test file green."
  Objective, resumable, parallel-safe.
- **`CONVENTIONS.md` first** (Phase 0) so fan-out agents produce uniform idioms *and* uniform
  Pythonic naming — re-linked from every task prompt.
- **Algorithm-faithful, Python-native**: translate the PHP logic and module structure closely (so
  agents can hold the source side-by-side and the goldens stay valid), but write idiomatic Python —
  `snake_case`, `@property`, dataclasses, `__getitem__`, top-level helpers — from the first pass. Do
  **not** preserve ArakneSwf's exact class/method names.
- **Parallelism**: Phase 2 (tag batches) and Phase 4 (subsystems) are the fan-out points — ~4–6 and
  ~3–5 agents respectively. Phases 0/1/5/6/7 are narrow/sequential gates.
- A `Workflow` (pipeline: port → verify-goldens per module) fits well if you want to orchestrate it
  end-to-end; otherwise dispatch one `Agent` per module slice per phase.

---

## 9. Risks & watch-items

| Risk | Mitigation |
|---|---|
| **SVG rasterizer fidelity** (filters, blur, gradients, blend modes) may differ from Imagick/rsvg | resvg default (closest to rsvg); isolate behind protocol; the "equivalent quality" bar tolerates minor diffs; visual-diff gate in Phase 6 |
| **XML-customization gap** — port can't write SWF; `custom_exports.py` relies on it | Explicit Phase 8 workstream (in-memory tag/timeline edits); keep ffdec for that step during transition |
| **Pure-Python performance** on large batches | Acceptable for offline asset builds; profile after correctness; Rust explicitly deferred |
| **Bitmap decode edge cases** (lossless color-table/alpha formats) | Pillow + fixture goldens for `image/`; Phase 4c has dedicated tests |
| **Fonts/Text tags** if Dofus gfx use `DefineText`/`DefineFont` | Full port includes them; goldens cover the `homestuck`/text fixtures |
| **Golden SVG comparison brittleness** (float formatting) | Nail normalization in Phase 0 before any drawer work |

---

## 10. Rough size

Port surface ≈ **~18–19k LOC** of PHP → Python (full src minus `Console` ~720 and minus the dropped
Converter output formats), across ~180 files. Fan-out-friendly; the golden suite makes each slice
independently verifiable.
