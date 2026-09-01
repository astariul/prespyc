"""
prespyc — SWF parsing and resource extraction in pure Python.

```python
import prespyc

swf = prespyc.open("1047.swf")

variables = swf.variables            # ActionScript 2 variables
sprite = swf.extractor["anim0R"]     # by exported name, or by character id
svg = sprite.to_svg()

# writes export/anim0R.webp + export/anim0R.json
prespyc.export("1047.swf", "anim0R", out_dir="export/", zoom=2)
```
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.errors import (
    CircularReferenceError,
    Errors,
    ExtractorError,
    ExtraDataError,
    InvalidDataError,
    OutOfBoundsError,
    ParserError,
    ProcessingInvalidDataError,
    SwfError,
    UnknownTagError,
)
from prespyc.output.exporter import export
from prespyc.swf_file import SwfFile

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "CircularReferenceError",
    "Errors",
    "ExtraDataError",
    "ExtractorError",
    "InvalidDataError",
    "OutOfBoundsError",
    "ParserError",
    "ProcessingInvalidDataError",
    "SwfError",
    "SwfFile",
    "UnknownTagError",
    "export",
    "open",
]


def open(path: Path | str, errors: int = Errors.ALL) -> SwfFile:
    """
    Open a SWF file. Nothing is read until you use it.

    `errors` selects which malformed-data conditions raise; see `Errors`. This shadows the builtin
    `open()` inside this module only — at a call site, `prespyc.open("x.swf")` is unambiguous.
    """
    return SwfFile(path, errors)
