"""`prespyc`-only: the gradient-ramp deviation from ArakneSwf."""

from __future__ import annotations

from prespyc.extractor.drawer.svg.svg_builder import ramp_records
from prespyc.parser.structure.record.color import Color
from prespyc.parser.structure.record.gradient_record import GradientRecord


def record(ratio: int, alpha: int = 255) -> GradientRecord:
    return GradientRecord(ratio, Color(1, 2, 3, alpha))


def test_strictly_increasing_ratios_are_all_kept():
    records = [record(0), record(121), record(255)]

    assert ramp_records(records) == records


def test_a_repeated_ratio_is_dropped():
    # What the Dofus gfx radial fills look like: the ramp ends on a duplicated
    # 255 carrying alpha 0. Flash never reaches it, so SVG must not pad with it.
    kept = record(255, 255)
    records = [record(121), kept, record(255, 0)]

    assert ramp_records(records) == [record(121), kept]


def test_a_decreasing_ratio_is_dropped():
    records = [record(0), record(200), record(100), record(255)]

    assert ramp_records(records) == [record(0), record(200), record(255)]


def test_no_records_stays_empty():
    assert ramp_records([]) == []
