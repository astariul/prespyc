"""Low-level SWF primitive reader."""

from __future__ import annotations

import struct
import zlib

from prespyc.errors import Errors, ExtraDataError, InvalidDataError, OutOfBoundsError

_UNPACK_UI32 = struct.Struct("<I").unpack_from
_UNPACK_SI64 = struct.Struct("<q").unpack_from
_UNPACK_F32 = struct.Struct("<f").unpack_from
_UNPACK_F64 = struct.Struct("<d").unpack


class Reader:
    """
    Reads SWF primitives from a binary buffer.

    Mutable and stateful: the read cursor lives on the instance, so a reader is never shared. Use
    `chunk()` to get an independent cursor over a slice of the same buffer.
    """

    __slots__ = ("_bit_offset", "_current_byte", "data", "end", "errors", "offset")

    def __init__(self, binary: bytes, end: int | None = None, errors: int = Errors.ALL) -> None:
        assert end is None or end <= len(binary)

        self.data: bytes = binary
        """Binary data of the SWF file."""

        self.end: int = len(binary) if end is None else end
        """End offset of the binary data (exclusive). Nothing can be read past it."""

        self.errors: int = int(errors)
        """Which malformed-data conditions raise instead of falling back. See `Errors`."""

        self.offset: int = 0
        """Current byte offset in the binary data."""

        self._bit_offset: int = 0
        """Bit offset inside the current byte, between 0 and 7."""

        self._current_byte: int = -1
        """
        Value of the byte being consumed bit by bit, or -1 when no byte is loaded.

        Must be reset to -1 after every change of `offset`.
        """

    # ------------------------------------------------------------------------------------ streams

    def uncompress(self, length: int | None = None) -> Reader:
        """
        Inflate the remaining data and return a new reader over it, positioned at the same offset.

        `length` caps the size of the uncompressed data, *including* the data already read.
        """
        offset = self.offset
        end = self.end
        data = bytearray(self.data[:offset])

        decompressor = zlib.decompressobj()
        failed = False

        while offset < end and not failed and not decompressor.eof:
            try:
                data += decompressor.decompress(self.data[offset : offset + 4096])
            except zlib.error:
                failed = True

            if length is not None and len(data) > length:
                break

            offset += 4096

        if length is not None and len(data) > length:
            if self.errors & Errors.EXTRA_DATA:
                raise ExtraDataError(
                    f"Uncompressed data exceeds the maximum length of {length} bytes (actual {len(data)} bytes)",
                    offset,
                    length,
                )

            data = data[:length]

        if not decompressor.eof and self.errors & Errors.INVALID_DATA:
            message = "Invalid compressed data: data error" if failed else "Truncated compressed data"

            raise InvalidDataError(message, offset)

        other = Reader(bytes(data), errors=self.errors)
        other.offset = self.offset

        return other

    def chunk(self, offset: int, end: int) -> Reader:
        """New reader over `[offset, end)` of the same buffer, with its own cursor."""
        assert end >= offset

        if end > self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(end, self.end)

            end = self.end

        other = Reader(self.data, end, self.errors)
        other.offset = offset

        return other

    # -------------------------------------------------------------------------------------- bytes

    def read_bytes(self, num: int) -> bytes:
        """Read `num` bytes."""
        assert self._bit_offset == 0

        offset = self.offset

        if offset + num > self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_too_many_bytes(offset, self.end, num)

            length = max(self.end - offset, 0)
            self.offset = self.end

            return self.data[offset : offset + length] + b"\0" * min(num - length, 128)

        self.offset = offset + num

        return self.data[offset : offset + num]

    def read_bytes_to(self, offset: int) -> bytes:
        """Read bytes up to `offset` (exclusive)."""
        assert self._bit_offset == 0

        current = self.offset

        if current == offset:
            return b""

        if offset < current:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError(
                    f"Cannot read bytes to an offset before the current offset: {offset} < {current}", offset
                )

            return b""

        if offset > self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(current, self.end)

            offset = self.end

        self.offset = offset

        return self.data[current:offset]

    def read_zlib_to(self, offset: int) -> bytes:
        """Read ZLib compressed bytes up to `offset` (exclusive) and inflate them."""
        compressed = self.read_bytes_to(offset)

        if compressed == b"":
            return b""

        try:
            return zlib.decompress(compressed)
        except zlib.error as error:
            if self.errors & Errors.INVALID_DATA:
                raise InvalidDataError.invalid_compressed_data(self.offset, str(error)) from error

            return b""

    def skip_bytes(self, num: int) -> None:
        """Advance the cursor by `num` bytes, without reading them."""
        assert self._bit_offset == 0

        self.offset += num

    def skip_to(self, offset: int) -> None:
        """Move the cursor to `offset`, which must not be before the current one."""
        assert self._bit_offset == 0
        assert offset >= self.offset

        self.offset = offset

    def read_char(self) -> bytes:
        """Read a single byte, as `bytes`. Equivalent to `read_bytes(1)`."""
        return self.read_ui8().to_bytes(1, "big")

    def read_null_terminated_string(self) -> bytes:
        """Read bytes up to the next null byte, which is consumed but not returned."""
        assert self._bit_offset == 0

        start = self.offset
        end = self.data.find(b"\0", start)

        if end == -1:
            if self.errors & Errors.INVALID_DATA:
                raise InvalidDataError("String terminator not found", start)

            self.offset = self.end

            return self.data[start : start + max(self.end - start, 0)]

        if end >= self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(start, self.end)

            self.offset = self.end

            return self.data[start : start + max(self.end - start, 0)]

        self.offset = end + 1

        return self.data[start:end]

    # --------------------------------------------------------------------------------------- bits

    def align_byte(self) -> None:
        """Drop the partially consumed byte. Must be called when done reading bits."""
        if self._bit_offset != 0:
            self.offset += 1
            self._bit_offset = 0
            self._current_byte = -1

    def read_ub(self, num: int) -> int:
        """Read `num` bits (0 to 32) as an unsigned integer."""
        if num == 0:
            return 0

        value = 0
        current_byte = self._current_byte
        bit_offset = self._bit_offset
        offset = self.offset
        data = self.data
        end = self.end

        while num > 0:
            if current_byte == -1:
                if offset >= end:
                    if self.errors & Errors.OUT_OF_BOUNDS:
                        raise OutOfBoundsError.read_after_end(offset, end)

                    current_byte = 0
                else:
                    current_byte = data[offset]

            remaining_bits = bits_to_read = 8 - bit_offset

            if bits_to_read > num:
                bits_to_read = num

            mask = (1 << bits_to_read) - 1
            segment = (current_byte >> (remaining_bits - bits_to_read)) & mask
            value |= segment << (num - bits_to_read)

            num -= bits_to_read
            bit_offset += bits_to_read

            if bit_offset >= 8:
                bit_offset = 0
                offset += 1
                current_byte = -1

        self._bit_offset = bit_offset
        self.offset = offset
        self._current_byte = current_byte

        return value

    def skip_bits(self, num: int) -> None:
        """Advance the cursor by `num` bits, without reading them."""
        new_offset = self._bit_offset + num

        if new_offset < 8:
            self._bit_offset = new_offset
        else:
            self.offset += new_offset >> 3
            self._bit_offset = new_offset & 7
            self._current_byte = -1

    def read_bool(self) -> bool:
        """Read a single bit. Equivalent to `read_ub(1) == 1`."""
        offset = self._bit_offset

        if self._current_byte == -1:
            byte_offset = self.offset

            if byte_offset >= self.end:
                if self.errors & Errors.OUT_OF_BOUNDS:
                    raise OutOfBoundsError.read_after_end(byte_offset, self.end)

                self._current_byte = 0
            else:
                self._current_byte = self.data[byte_offset]

        mask = 1 << (7 - offset)
        ret = (self._current_byte & mask) == mask
        offset += 1

        if offset < 8:
            self._bit_offset = offset
        else:
            self.offset += 1
            self._bit_offset = 0
            self._current_byte = -1

        return ret

    def read_sb(self, num: int) -> int:
        """Read `num` bits (0 to 32) as a two's complement signed integer."""
        if num == 0:
            return 0

        value = self.read_ub(num)

        if value & (1 << (num - 1)) == 0:
            return value

        return value - (1 << num)

    def read_fb(self, num: int) -> float:
        """
        Read `num` bits as a signed 16.16 fixed point number.

        The low 16 bits hold the fractional part, the high bits the integer part, and the topmost
        bit is the sign. With fewer than 17 bits the value is purely fractional.
        """
        if num == 0:
            return 0.0

        assert num <= 32

        raw = self.read_ub(num)

        if raw & (1 << (num - 1)) == 0:
            return ((raw >> 16) & 0xFFFF) + (raw & 0xFFFF) / 65536.0

        raw = (1 << num) - raw

        return -(((raw >> 16) & 0xFFFF) + (raw & 0xFFFF) / 65536.0)

    # ------------------------------------------------------------------------------------ numbers

    def read_fixed8(self) -> float:
        """Read a signed 8.8 fixed point number."""
        return self.read_si16() / 256.0

    def read_fixed(self) -> float:
        """Read a signed 16.16 fixed point number."""
        return self.read_si32() / 65536.0

    def read_float16(self) -> float:
        """
        Read a 16 bit half precision float.

        SWF uses 1 sign bit, 5 exponent bits with a bias of 16 (*not* the IEEE 754 bias) and 10
        mantissa bits.
        """
        raw = self.read_ui8() | (self.read_ui8() << 8)

        sign = (raw >> 15) & 0x0001
        exponent = (raw >> 10) & 0x001F
        mantissa = raw & 0x03FF

        if exponent == 0 and mantissa == 0:
            return 0.0 if sign == 0 else -0.0

        if exponent == 0:
            # Denormalized number
            return (1.0 if sign == 0 else -1.0) * (2**-15) * mantissa / 1024.0

        if exponent == 0x1F:
            if mantissa != 0:
                return float("nan")

            return float("inf") if sign == 0 else float("-inf")

        ret = 1.0 if sign == 0 else -1.0

        if exponent > 16:
            ret *= 1 << (exponent - 16)
        else:
            ret /= 1 << (16 - exponent)

        return ret * (1.0 + mantissa / 1024.0)

    def read_float(self) -> float:
        """Read a 32 bit float."""
        return self._read_unpack(_UNPACK_F32, 4)

    def read_double(self) -> float:
        """Read a 64 bit double. SWF stores the two 32 bit words in reverse order."""
        low = self.read_bytes(4)
        high = self.read_bytes(4)

        return _UNPACK_F64(high + low)[0]

    def read_ui8(self) -> int:
        """Read a single byte as an unsigned integer."""
        assert self._bit_offset == 0

        offset = self.offset

        if offset >= self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(offset, self.end)

            return 0

        self.offset = offset + 1

        return self.data[offset]

    def read_si16(self) -> int:
        """Read two bytes as a signed integer."""
        ret = self.read_ui8() | (self.read_ui8() << 8)

        if ret >= 32768:
            ret -= 65536

        return ret

    def read_ui16(self) -> int:
        """Read two bytes as an unsigned integer."""
        return self.read_ui8() | (self.read_ui8() << 8)

    def peek_ui16(self) -> int:
        """Read two bytes as an unsigned integer, without moving the cursor."""
        offset = self.offset

        if offset + 1 >= self.end:
            if self.errors & Errors.OUT_OF_BOUNDS:
                raise OutOfBoundsError.read_after_end(offset, self.end)

            # Not consistent with read_ui16(), but it does the job
            return 0

        return self.data[offset] | (self.data[offset + 1] << 8)

    def read_si32(self) -> int:
        """Read four bytes as a signed integer."""
        value = self.read_ui32()

        if value >= 2147483648:
            value -= 4294967296

        return value

    def read_ui32(self) -> int:
        """Read four bytes as an unsigned integer."""
        return self._read_unpack(_UNPACK_UI32, 4)

    def read_si64(self) -> int:
        """Read eight bytes as a signed integer."""
        return self._read_unpack(_UNPACK_SI64, 8)

    def read_encoded_u32(self) -> int:
        """Read a variable length unsigned integer, between 1 and 5 bytes, as a 32 bit value."""
        result = self.read_ui8()
        if result & 0x00000080 == 0:
            return result

        result = (result & 0x0000007F) | (self.read_ui8() << 7)
        if result & 0x00004000 == 0:
            return result

        result = (result & 0x00003FFF) | (self.read_ui8() << 14)
        if result & 0x00200000 == 0:
            return result

        result = (result & 0x001FFFFF) | (self.read_ui8() << 21)
        if result & 0x10000000 == 0:
            return result

        return (result & 0x0FFFFFFF) | (self.read_ui8() << 28)

    def _read_unpack(self, unpack, size: int):
        assert self._bit_offset == 0

        offset = self.offset

        if offset + size <= self.end:
            self.offset = offset + size

            return unpack(self.data, offset)[0]

        if self.errors & Errors.OUT_OF_BOUNDS:
            raise OutOfBoundsError.read_too_many_bytes(offset, self.end, size)

        value = unpack(self.read_bytes(size), 0)[0]
        self.offset = self.end

        return value
