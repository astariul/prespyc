# CONVENTIONS

`prespyc` is a port of [ArakneSwf](https://github.com/Arakne/ArakneSwf) (PHP) to Python.

Two rules govern every file:

1. **Algorithm-faithful.** Keep the PHP control flow, branch order, arithmetic and module split.
   The ~1,130 golden SVGs are the oracle; a "cleaner" rewrite that changes rounding or branch
   order breaks them.
2. **Python-native surface.** `snake_case`, dataclasses, properties, `__getitem__`, generators.
   No PHP-isms leak into the public API. Do *not* keep ArakneSwf's identifiers.

---

## 1. Module map

| PHP | Python |
|---|---|
| `Arakne\Swf\SwfFile` | `prespyc.swf_file.SwfFile` |
| `Arakne\Swf\Error\Errors` | `prespyc.errors.Errors` |
| `Arakne\Swf\Parser\SwfReader` | `prespyc.parser.reader.Reader` |
| `Arakne\Swf\Parser\Swf` | `prespyc.parser.swf.Swf` |
| `Arakne\Swf\Parser\Structure\SwfHeader` | `prespyc.parser.structure.header.Header` |
| `Arakne\Swf\Parser\Structure\SwfTag` | `prespyc.parser.structure.raw_tag.RawTag` |
| `Arakne\Swf\Parser\Structure\Tag\XxxTag` | `prespyc.parser.structure.tag.xxx.XxxTag` |
| `Arakne\Swf\Parser\Structure\Record\Xxx` | `prespyc.parser.structure.record.xxx.Xxx` |
| `Arakne\Swf\Parser\Structure\Action\Xxx` | `prespyc.parser.structure.action.xxx.Xxx` |
| `Arakne\Swf\Avm\Processor` | `prespyc.avm.processor.Processor` |
| `Arakne\Swf\Extractor\SwfExtractor` | `prespyc.extractor.extractor.Extractor` |
| `Arakne\Swf\Extractor\Drawer\DrawerInterface` | `prespyc.extractor.drawer.drawer.Drawer` (Protocol) |
| `Arakne\Swf\Extractor\Drawer\Svg\*` | `prespyc.extractor.drawer.svg.*` |
| `Arakne\Swf\Extractor\Drawer\Converter\*` | `prespyc.extractor.drawer.converter` + `.render.*` |
| `Arakne\Swf\Console\*` | **dropped** (no CLI) |

Module file names are `snake_case` of the PHP class name: `DefineBitsJPEG3Tag.php` →
`define_bits_jpeg3.py`, `PlaceObject2Tag.php` → `place_object2.py`, `MorphShapeProcessor.php` →
`morph_shape_processor.py`.

Sub-package `__init__.py` files stay **empty**: import full module paths
(`from prespyc.parser.structure.tag.define_shape import DefineShapeTag`). With ~180 modules,
re-export shims buy little and invite import cycles. The only curated surface is the top-level
`prespyc/__init__.py` (§7 of `PLAN.md`).

## 2. Naming

| PHP | Python |
|---|---|
| `$camelCase` field | `snake_case` field |
| `readUI16()` | `read_ui16()` (acronyms stay lowercase: `ui8`, `si32`, `ub`, `sb`, `fb`, `rgba`) |
| `getFoo()` / `foo()` accessor with no args | `@property foo` |
| `framesCount(bool $recursive)` | `frames_count(recursive: bool = False)` — stays a method (it takes args) |
| `character(int $id)` | `Extractor.__getitem__` **and** `character(id)`; `__getitem__` accepts `int` id or `str` name |
| `byName(string $name)` | `by_name(name)` |
| `exported()` | `@property exported` |
| `toSvg()` / `toWebp()` | `to_svg()` / `to_webp()` |
| `XxxInterface` | `Xxx` (a `typing.Protocol`, or ABC when it holds shared code) |
| `AbstractXxx` | `BaseXxx` |
| `XxxException` | `XxxError` |
| enum `Opcode` | `enum.IntEnum` / `enum.Enum` with `UPPER_SNAKE` members |
| `const int TYPE = 2` | `TYPE: ClassVar[int] = 2` |

Suffixes that carry SWF-spec meaning are kept: `...Tag`, `...Record`, `...Definition`, `...Style`.

## 3. Idiom mapping

| PHP | Python |
|---|---|
| `final readonly class` (value object) | `@dataclass(frozen=True, slots=True)` |
| stateful `final class` | plain class with `__slots__` |
| `public static function read(SwfReader $r): self` | `@classmethod def read(cls, reader: Reader) -> Self` |
| `unpack('V', $s)` | `struct.unpack_from` / `int.from_bytes(..., "little")` |
| `pack(...)` | `struct.pack` (tests only — the port never writes SWF) |
| `gzuncompress` | `zlib.decompress` |
| `inflate_init` + `inflate_add` | `zlib.decompressobj()` |
| `strlen`, `substr`, `strpos` on binary | `len`, slicing, `bytes.find` on **`bytes`** |
| `$data[$i]` (1-char string) | `data[i]` (**int**) — no `ord()` needed |
| `ord($r->readChar())` | `reader.read_ui8()` |
| `iterable` + `yield` | generator function |
| `match ($x) { ... }` | `match`/`case`, or a module-level dict when it is a pure lookup |
| `array<string, T>` | `dict[str, T]` |
| `list<T>` | `list[T]` |
| `?int $x = null` | `x: int \| None = None` |
| `$a ??= b` | `if a is None: a = b` |
| `assert(...)` | `assert ...` (same role: developer invariant, not validation) |
| `PHP_INT_MAX` | `sys.maxsize` — but prefer `math.inf` / `None` when it is a "no value yet" sentinel and the result is compared, never returned |
| `static::$cache` memoisation | instance attribute set lazily, or `functools.cached_property` |

Binary data is always `bytes`, never `str`. Text decoded from SWF is `str` (see §6).

## 4. Numbers — the fidelity traps

PHP semantics that differ from Python and **change golden output**. Always use the helpers from
`prespyc._util`:

| PHP | Python | Helper |
|---|---|---|
| `round($v)` | half **away from zero** (Python rounds half to even) | `php_round(v)` |
| `round($v, 4)` | half away from zero, 4 decimals | `php_round(v, 4)` |
| `(int) $v` on float | truncate **toward zero** (Python `int()` matches) | `int(v)` — fine as is |
| `(int) round($v)` | | `round_int(v)` |
| `intdiv($a, $b)` | truncates toward zero (Python `//` floors) | `int(a / b)` or `php_intdiv(a, b)` |
| `$a % $b` | sign follows the dividend (Python follows the divisor) | `php_mod(a, b)` |
| `$a >> $b` on negatives | arithmetic shift (Python matches) | `a >> b` — fine as is |
| string interpolation of a float | `%.14G` then cleanup: `1.0` → `"1"`, `-0.0` → `"-0"` | `num(v)` |
| `sprintf('%02x', ...)` | `f"{v:02x}"` | — |

`num()` is mandatory for every number written into SVG output. `"1.0"` where PHP wrote `"1"` is a
golden failure.

Integer width: PHP is 64-bit and wraps nothing in practice here; Python ints are unbounded. Where
the PHP code relies on 32-bit wrap (AVM bitwise ops), mask explicitly — `to_int32()` in
`prespyc._util`.

## 5. Errors

`Errors` is an `enum.IntFlag`. Flag semantics are unchanged: a set bit means *raise*, a clear bit
means *return the fallback value and continue*. Always write the PHP shape:

```python
if reader.errors & Errors.OUT_OF_BOUNDS:
    raise OutOfBoundsError.read_after_end(offset, end)
# fallback path
```

Exception hierarchy (all in `prespyc.errors`):

```
SwfError(Exception)
├── ParserError(SwfError)          .offset
│   ├── OutOfBoundsError           (was ParserOutOfBoundException)
│   ├── InvalidDataError           (was ParserInvalidDataException)
│   ├── ExtraDataError             (was ParserExtraDataException)  .length
│   └── UnknownTagError            (was UnknownTagException)      .tag_code
└── ExtractorError(SwfError)
    ├── CircularReferenceError
    └── ProcessingInvalidDataError
```

Named constructors (`ParserOutOfBoundException::createReadAfterEnd`) become `@classmethod`s with
`snake_case` names (`OutOfBoundsError.read_after_end`). Messages are copied **verbatim** from PHP —
tests assert on them.

## 6. Strings

SWF stores text as bytes: Latin-1 for SWF < 6, UTF-8 for SWF >= 6. Follow the PHP code: it mostly
keeps raw bytes and only decodes where the original does. When a `str` is required, use
`decode_swf_text(raw, swf_version)` from `prespyc._util` (`utf-8` with `errors="replace"` for
version >= 6, `latin-1` otherwise) — never a bare `.decode()`.

## 7. Tests

- One pytest module per PHPUnit class: `tests/Parser/SwfReaderTest.php` →
  `tests/parser/test_reader.py`. Test method `readUI8` → `def test_read_ui8()`.
- Plain functions + `pytest.mark.parametrize`, no test classes.
- PHPUnit → pytest:
  | PHPUnit | pytest |
  |---|---|
  | `assertSame` | `assert a == b` (`is` only for identity assertions — `assertSame($a->x(), $a->x())` on objects means *the same cached instance*) |
  | `assertEquals` | `assert a == b` (dataclass equality) |
  | `assertEqualsWithDelta` | `assert a == pytest.approx(b, abs=delta)` |
  | `expectException` | `pytest.raises` |
  | `assertXmlStringEqualsXmlFile` | `assert_svg_matches(svg, path)` from `tests/support.py` |
  | `assertXmlStringEqualsXmlString` | `assert_svg_equals(svg, expected)` |
  | `assertImageStringEqualsImageFile` | `assert_image_matches(blob, path)` |
- Fixtures live in `tests/fixtures/`, mirroring the PHP layout:
  `tests/Extractor/Fixtures/x` → `tests/fixtures/extractor/x`, `tests/Parser/Fixtures/x` →
  `tests/fixtures/parser/x`, `tests/Fixtures/x` → `tests/fixtures/x`.
  Use `fixture()` / `fixture_reader()` from `tests/support.py` and the `swf_builder` pytest fixture, never
  hardcoded paths.

## 8. Style

- Type-annotate every public signature. `from __future__ import annotations` at the top of every
  module.
- Docstrings: port the PHP docblock prose when it explains *why* or documents a spec quirk. Drop
  `@param`/`@return` boilerplate that the annotations already say.
- Keep the PHP comments that flag spec oddities, bug workarounds or offset arithmetic.
- `ruff check .` and `ruff format`-compatible formatting (line length 120).
- No new runtime dependency without changing `pyproject.toml` in the same commit.
