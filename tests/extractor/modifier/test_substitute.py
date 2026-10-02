"""The `Substitute` modifier: characters swapped by id, through the whole tree."""

from __future__ import annotations

from prespyc.extractor.modifier.substitute import Substitute
from prespyc.swf_file import SwfFile
from tests.support import fixture


def test_substitute_through_the_tree() -> None:
    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor
    original = extractor[65].timeline.frames[0].objects[11]  # sprite 13, placed by 65, placed by 66
    foot = extractor[15]

    static = extractor[66].modify(Substitute({13: foot}))

    [placed] = static.timeline.frames[0].objects.values()
    swapped = placed.object.timeline.frames[0].objects[11]

    assert swapped.object is foot
    assert swapped.matrix == original.tag_matrix.translate(foot.bounds.xmin, foot.bounds.ymin)
    assert swapped.color_transform == original.color_transform


def test_substitute_the_drawable_itself() -> None:
    extractor = SwfFile(fixture("extractor", "1047", "1047.swf")).extractor

    assert extractor[13].modify(Substitute({13: extractor[15]})) is extractor[15]
