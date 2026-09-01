"""DefineSceneAndFrameLabelData tag: the scene and frame label table of the main timeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class DefineSceneAndFrameLabelDataTag:
    """Scene names by start frame, and frame labels by frame number."""

    TYPE: ClassVar[int] = 86

    scene_offsets: list[int]
    scene_names: list[bytes]
    frame_numbers: list[int]
    frame_labels: list[bytes]

    @classmethod
    def read(cls, reader: Reader) -> Self:
        scene_offsets: list[int] = []
        scene_names: list[bytes] = []
        scene_count = reader.read_encoded_u32()

        for _ in range(scene_count):
            if reader.offset >= reader.end:
                break

            scene_offsets.append(reader.read_encoded_u32())
            scene_names.append(reader.read_null_terminated_string())

        frame_numbers: list[int] = []
        frame_labels: list[bytes] = []
        frame_label_count = reader.read_encoded_u32()

        for _ in range(frame_label_count):
            if reader.offset >= reader.end:
                break

            frame_numbers.append(reader.read_encoded_u32())
            frame_labels.append(reader.read_null_terminated_string())

        return cls(
            scene_offsets=scene_offsets,
            scene_names=scene_names,
            frame_numbers=frame_numbers,
            frame_labels=frame_labels,
        )
