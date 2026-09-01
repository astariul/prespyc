"""Entry point: a SWF file on disk."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from prespyc.errors import Errors, ParserError
from prespyc.parser.reader import Reader
from prespyc.parser.swf import Swf

if TYPE_CHECKING:
    from collections.abc import Iterator

    from prespyc.avm.processor import Processor
    from prespyc.avm.state import State
    from prespyc.extractor.extractor import Extractor
    from prespyc.extractor.timeline.timeline import Timeline
    from prespyc.parser.structure.header import Header
    from prespyc.parser.structure.raw_tag import RawTag
    from prespyc.parser.structure.record.rectangle import Rectangle

MAX_FRAME_RATE = 120
"""
A frame rate of 0 means "as fast as possible", which we cap here.

See https://www.m2osw.com/swf_tag_file_header#comment-1345. Negative values are possible because
the field is a fixed8, but older specs define it as a UI16, so they are treated as 0 too.
"""


class SwfFile:
    """
    A SWF file. Parsing is lazy: nothing is read until a member is used.

    `errors` selects which malformed-data conditions raise. Enabling everything stops on the first
    malformed or unexpected byte, which is safer but fails on some legitimate files; disabling
    everything extracts as much as possible from a corrupted file, at the cost of unexpected
    results.
    """

    __slots__ = ("_extractor", "_parser", "errors", "path")

    def __init__(self, path: Path | str, errors: int = Errors.ALL) -> None:
        self.path = Path(path)
        self.errors = int(errors)
        self._parser: Swf | None = None
        self._extractor: Extractor | None = None

    def valid(self, max_length: int = 512_000_000) -> bool:
        """
        Whether the file looks like a SWF file.

        Only the header is checked, so the body may still be corrupted or incomplete.
        `max_length` caps the decompressed size, in bytes.
        """
        try:
            with self.path.open("rb") as file:
                head = file.read(8)
        except OSError:
            return False

        if len(head) < 8:
            return False

        reader = Reader(head)

        if reader.read_bytes(3) not in (b"CWS", b"FWS"):
            return False

        # The last version (2024) is 51, so anything above 60 is safely invalid.
        if reader.read_ui8() > 60:
            return False

        return reader.read_ui32() <= max_length

    @property
    def header(self) -> Header:
        return self._parse().header

    @property
    def display_bounds(self) -> Rectangle:
        """Display size of the file's frames, in twips."""
        return self._parse().header.frame_size

    @property
    def frame_rate(self) -> int:
        """Frame rate of the file, clamped to `MAX_FRAME_RATE`."""
        rate = int(self._parse().header.frame_rate)

        if rate <= 0:
            return MAX_FRAME_RATE

        return MAX_FRAME_RATE if rate > MAX_FRAME_RATE else rate

    def tags(self, *tag_types: int) -> Iterator[tuple[RawTag, Any]]:
        """
        Iterate over the tags, as `(raw tag, parsed tag)` pairs.

        Without arguments, every tag is yielded; otherwise only the given tag types. The raw tag
        carries the byte range and, for definition tags, the character id.
        """
        parser = self._parse()
        ignore_invalid_tags = (self.errors & Errors.INVALID_TAG) == 0
        wanted = frozenset(tag_types)

        for tag in parser.tags:
            if wanted and tag.type not in wanted:
                continue

            try:
                parsed = parser.parse(tag)
            except ParserError:
                if not ignore_invalid_tags:
                    raise

                continue

            yield tag, parsed

    def execute(self, state: State | None = None, processor: Processor | None = None) -> State:
        """
        Run the `DoAction` tags and return the final state.

        Dangerous on untrusted files: call it only on a source you trust. Function calls are
        disabled unless you pass a `Processor` built with `allow_function_call=True`.
        """
        from prespyc.avm.processor import Processor as DefaultProcessor
        from prespyc.avm.state import State as DefaultState
        from prespyc.parser.structure.tag.do_action import DoActionTag

        if processor is None:
            processor = DefaultProcessor(allow_function_call=False)

        if state is None:
            state = DefaultState()

        # TODO handle DoInitActionTag
        for _, tag in self.tags(DoActionTag.TYPE):
            state = processor.run(tag.actions, state)

        return state

    @property
    def variables(self) -> dict[str, Any]:
        """
        Global variables left by the `DoAction` tags.

        Same caveat as `execute()`: only run this on a file you trust. Use
        `execute(state, processor).variables` when you need a custom state or a processor that
        allows function calls.
        """
        return self.execute().variables

    @property
    def extractor(self) -> Extractor:
        """
        The asset extractor for this file, created once and cached.

        ArakneSwf builds a fresh extractor per call instead, to avoid retaining its caches. Here the
        instance is shared, so repeated lookups reuse the processed characters; call
        `extractor.release()` to free them.
        """
        from prespyc.extractor.extractor import Extractor

        if self._extractor is None:
            self._extractor = Extractor(self)

        return self._extractor

    @property
    def exported_assets(self) -> dict[str, Any]:
        """Every exported asset, indexed by exported name."""
        extractor = self.extractor

        return {name: extractor.character(id) for name, id in extractor.exported.items()}

    def asset_by_name(self, name: str):
        """The asset exported under `name`. Raises `KeyError` when it is not exported."""
        return self.extractor.by_name(name)

    def asset_by_id(self, id: int):
        """The asset with character id `id`, or a `MissingCharacter` when there is none."""
        return self.extractor.character(id)

    def timeline(self, use_file_display_bounds: bool = True) -> Timeline:
        """
        The root timeline animation.

        With `use_file_display_bounds`, the timeline is sized to `display_bounds`; otherwise to the
        union of every frame's bounds.
        """
        return self.extractor.timeline(use_file_display_bounds)

    def _parse(self) -> Swf:
        if self._parser is None:
            self._parser = Swf.from_bytes(self.path.read_bytes(), self.errors)

        return self._parser
