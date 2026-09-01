"""The `gotoAndStop()` action, as a character modifier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prespyc.extractor.modifier.base_character_modifier import BaseCharacterModifier

if TYPE_CHECKING:
    from prespyc.extractor.timeline.timeline import Timeline


class GotoAndStop(BaseCharacterModifier):
    """
    Performs the `gotoAndStop()` action on a character timeline.

    Keeps the frame with the given label, or the one at the given number.
    """

    __slots__ = ("_frame",)

    def __init__(self, frame: int | str) -> None:
        self._frame = frame
        """
        Frame label or number to go to and stop at. A label that is not found falls back to the
        first frame.
        """

    def apply_on_timeline(self, timeline: Timeline) -> Timeline:
        if isinstance(self._frame, str):
            return timeline.keep_frame_by_label(self._frame)

        return timeline.keep_frame_by_number(self._frame)
