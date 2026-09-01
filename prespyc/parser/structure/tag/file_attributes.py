"""FileAttributes tag: the player capabilities the file requires."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from prespyc.parser.reader import Reader


@dataclass(frozen=True, slots=True)
class FileAttributesTag:
    """Flags telling the player which features the file uses. Must be the first tag of the file."""

    TYPE: ClassVar[int] = 69

    use_direct_blit: bool
    use_gpu: bool
    has_metadata: bool
    action_script3: bool
    use_network: bool

    @classmethod
    def read(cls, reader: Reader) -> Self:
        flags = reader.read_ui8()
        # 1 bit reserved, must be 0
        use_direct_blit = (flags & 0b01000000) != 0
        use_gpu = (flags & 0b00100000) != 0
        has_metadata = (flags & 0b00010000) != 0
        action_script3 = (flags & 0b00001000) != 0
        # 2 bits reserved, must be 0
        use_network = (flags & 0b00000001) != 0

        reader.skip_bytes(3)  # Reserved, must be 0

        return cls(
            use_direct_blit=use_direct_blit,
            use_gpu=use_gpu,
            has_metadata=has_metadata,
            action_script3=action_script3,
            use_network=use_network,
        )
