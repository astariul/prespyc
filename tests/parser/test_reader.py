"""Port of ArakneSwf's `tests/Parser/SwfReaderTest.php`."""

from __future__ import annotations

import math
import random
import re
import zlib

import pytest

from prespyc._util import num
from prespyc.errors import Errors, ExtraDataError, InvalidDataError, OutOfBoundsError
from prespyc.parser.reader import Reader
from tests.support import fixture, fixture_reader


def test_read_bytes():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())

    assert reader.read_bytes(3) == b"FWS"
    assert reader.offset == 3
    assert reader.read_bytes(2) == b"\x11\x32"
    assert reader.offset == 5


def test_read_bytes_overflow():
    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 2")):
        Reader(b"abcd", 2).read_bytes(4)


def test_read_bytes_overflow_ignore_error():
    assert Reader(b"abcd", 2, Errors.NONE).read_bytes(4) == b"ab\0\0"


def test_uncompress():
    data = b"CWF\x05\xff\x00\x00\x00" + zlib.compress(b"a" * 247)
    reader = Reader(data)
    reader.skip_bytes(8)

    new_reader = reader.uncompress(255)

    assert new_reader is not reader
    assert new_reader.offset == 8
    assert new_reader.data == b"CWF\x05\xff\x00\x00\x00" + b"a" * 247


def test_uncompress_end_stream_detection():
    reader = Reader(fixture("parser", "95.swf").read_bytes())
    reader.skip_bytes(8)
    reader = reader.uncompress(5183)

    assert reader.end == 5183
    assert reader.offset == 8


def test_uncompress_without_length():
    data = b"CWF\x05\xff\x00\x00\x00" + zlib.compress(b"a" * 247)
    reader = Reader(data)
    reader.skip_bytes(8)

    new_reader = reader.uncompress()

    assert new_reader is not reader
    assert new_reader.offset == 8
    assert new_reader.data == b"CWF\x05\xff\x00\x00\x00" + b"a" * 247


def test_uncompress_data_too_long():
    data = b"CWF\x05\xff\x00\x00\x00" + zlib.compress(b"a" * 247)
    reader = Reader(data)
    reader.skip_bytes(8)

    with pytest.raises(
        ExtraDataError, match=re.escape("Uncompressed data exceeds the maximum length of 100 bytes (actual 255 bytes)")
    ):
        reader.uncompress(100)


def test_uncompress_zip_bomb():
    data = b"CWF\x05\xff\x00\x00\x00" + zlib.compress(b"a" * 10_000_000)
    reader = Reader(data)
    reader.skip_bytes(8)

    with pytest.raises(
        ExtraDataError,
        match=re.escape("Uncompressed data exceeds the maximum length of 5000 bytes (actual 4209796 bytes)"),
    ):
        reader.uncompress(5000)


def test_uncompress_data_too_long_ignore_error():
    data = b"CWF\x05\xff\x00\x00\x00" + zlib.compress(b"a" * 247)
    reader = Reader(data, errors=Errors.NONE)
    reader.skip_bytes(8)

    reader = reader.uncompress(100)

    assert reader.data == b"CWF\x05\xff\x00\x00\x00" + b"a" * 92


def test_uncompress_invalid_data():
    data = b"CWF\x05\xff\x00\x00\x00invalid data"
    reader = Reader(data)
    reader.skip_bytes(8)

    with pytest.raises(InvalidDataError, match=re.escape("Invalid compressed data: data error")):
        reader.uncompress()


def test_uncompress_invalid_data_ignore_error():
    data = b"CWF\x05\xff\x00\x00\x00invalid data"
    reader = Reader(data, errors=Errors.NONE)
    reader.skip_bytes(8)
    reader = reader.uncompress()

    assert reader.data == b"CWF\x05\xff\x00\x00\x00"


def test_uncompress_invalid_checksum():
    compressed = bytearray(zlib.compress(b"a" * 247))
    compressed[5] = ord("0")

    data = b"CWF\x05\xff\x00\x00\x00" + bytes(compressed)
    reader = Reader(data)
    reader.skip_bytes(8)

    with pytest.raises(InvalidDataError, match=re.escape("Invalid compressed data: data error")):
        reader.uncompress()


def test_uncompress_invalid_checksum_ignore_error():
    original = random.Random(123).randbytes(10000)
    compressed = bytearray(zlib.compress(original))
    compressed[8300] = ord("0")

    data = b"CWF\x05\xff\x00\x00\x00" + bytes(compressed)
    reader = Reader(data, errors=Errors.NONE)
    reader.skip_bytes(8)
    reader = reader.uncompress()

    length = len(reader.data)
    assert length < 10000
    assert length > 4000
    assert reader.data == (b"CWF\x05\xff\x00\x00\x00" + original)[:length]


def test_uncompress_truncated_data():
    compressed = zlib.compress(b"a" * 247)
    compressed = compressed[: int(0.9 * len(compressed))]

    data = b"CWF\x05\xff\x00\x00\x00" + compressed
    reader = Reader(data)
    reader.skip_bytes(8)

    with pytest.raises(InvalidDataError, match=re.escape("Truncated compressed data")):
        reader.uncompress()


def test_uncompress_truncated_data_ignore_error():
    compressed = zlib.compress(b"abcdefghijklmnopqrstuvwxyz" * 10)
    compressed = compressed[: int(0.7 * len(compressed))]

    data = b"CWF\x05\xff\x00\x00\x00" + compressed
    reader = Reader(data, errors=Errors.NONE)
    reader.skip_bytes(8)
    reader = reader.uncompress()

    assert reader.data == b"CWF\x05\xff\x00\x00\x00abcdefghijklmnopqrstuv"


def test_chunk():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz")
    reader.skip_bytes(3)

    chunk = reader.chunk(10, 15)

    assert chunk is not reader
    assert chunk.offset == 10
    assert reader.offset == 3


def test_chunk_overflow():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 13)

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 15, end: 13)"),
    ):
        reader.chunk(10, 15)


def test_chunk_overflow_ignore_error():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 13, Errors.NONE)
    chunk = reader.chunk(10, 15)

    assert chunk.offset == 10
    assert chunk.end == 13


def test_read_bytes_to():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz")

    assert reader.read_bytes_to(4) == b"abcd"
    assert reader.offset == 4

    assert reader.read_bytes_to(8) == b"efgh"
    assert reader.offset == 8

    assert reader.read_bytes_to(8) == b""
    assert reader.offset == 8

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Cannot read bytes to an offset before the current offset: 5 < 8")
    ):
        reader.read_bytes_to(5)

    assert reader.offset == 8


def test_read_bytes_to_overflow():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 10)

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 0, end: 10)"),
    ):
        reader.read_bytes_to(11)


def test_read_bytes_to_overflow_ignore_error():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 10, Errors.NONE)

    assert reader.read_bytes_to(11) == b"abcdefghij"


def test_read_zlib_to():
    reader = Reader(zlib.compress(b"abcdefghijklmnopqrstuvwxyz"))

    assert reader.read_zlib_to(reader.end) == b"abcdefghijklmnopqrstuvwxyz"


def test_read_zlib_to_empty():
    reader = Reader(b"")

    assert reader.read_zlib_to(reader.end) == b""


def test_read_zlib_to_overflow():
    reader = Reader(zlib.compress(b"abcdefghijklmnopqrstuvwxyz"))

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 0, end: 34)"),
    ):
        reader.read_zlib_to(50)


def test_read_zlib_to_overflow_ignore_error():
    reader = Reader(zlib.compress(b"abcdefghijklmnopqrstuvwxyz"), errors=Errors.NONE)

    assert reader.read_zlib_to(50) == b"abcdefghijklmnopqrstuvwxyz"


def test_read_zlib_to_invalid_zlib_data():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz")

    # PHP appends the `gzuncompress()` warning; Python appends the `zlib` error text.
    with pytest.raises(InvalidDataError, match=re.escape("Invalid compressed data at offset 26: ")):
        reader.read_zlib_to(26)


def test_read_zlib_to_invalid_zlib_data_ignore_error():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", errors=Errors.NONE)

    assert reader.read_zlib_to(26) == b""


def test_skip_bytes():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())

    reader.skip_bytes(3)
    assert reader.offset == 3
    reader.skip_bytes(2)
    assert reader.offset == 5
    assert reader.read_ui8() == 194


def test_skip_to():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())

    reader.skip_bytes(3)
    assert reader.offset == 3
    reader.skip_to(25)
    assert reader.offset == 25


def test_read_char():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())

    assert reader.read_char() == b"F"
    assert reader.offset == 1
    assert reader.read_char() == b"W"
    assert reader.offset == 2
    assert reader.read_char() == b"S"


def test_read_char_overflow():
    reader = Reader(b"abc", 2)
    reader.skip_bytes(2)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_char()


def test_read_char_overflow_ignore_error():
    reader = Reader(b"abc", 2, Errors.NONE)
    reader.skip_bytes(2)

    assert reader.read_char() == b"\0"


def test_read_ub():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(8)

    assert reader.read_ub(5) == 16
    assert reader.offset == 8

    assert reader.read_ub(16) == 0
    assert reader.offset == 10

    assert reader.read_ub(16) == 13300
    assert reader.offset == 12

    assert reader.read_ub(16) == 0
    assert reader.offset == 14

    assert reader.read_ub(16) == 17600
    assert reader.offset == 16

    assert reader.read_ub(0) == 0
    assert reader.offset == 16

    assert reader.read_ub(3) == 0
    assert reader.offset == 17


def test_read_ub_overflow():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 2)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_ub(17)


def test_read_ub_overflow_ignore_error():
    reader = Reader(b"abcdefghijklmnopqrstuvwxyz", 2, Errors.NONE)

    assert reader.read_ub(17) == 49860


def test_skip_bits():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(8)
    reader.skip_bits(21)
    assert reader.offset == 10

    assert reader.read_ub(16) == 13300


def test_align_byte():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(8)

    reader.align_byte()
    assert reader.offset == 8

    reader.skip_bits(21)
    reader.align_byte()
    assert reader.offset == 11


def test_read_null_terminated_string():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(573)
    assert reader.read_null_terminated_string() == b"_184_fla.MainTimeline"

    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(59)
    assert reader.read_null_terminated_string() == b""


def test_read_null_terminated_string_overflow():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes(), 580)
    reader.skip_bytes(573)

    with pytest.raises(
        OutOfBoundsError,
        match=re.escape("Trying to access data after the end of the input stream (offset: 573, end: 580)"),
    ):
        reader.read_null_terminated_string()


def test_read_null_terminated_string_overflow_ignore_error():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes(), 580, Errors.NONE)
    reader.skip_bytes(573)

    assert reader.read_null_terminated_string() == b"_184_fl"


def test_read_null_terminated_string_missing_null():
    reader = Reader(b"foo bar")

    with pytest.raises(InvalidDataError, match=re.escape("String terminator not found")):
        reader.read_null_terminated_string()


def test_read_null_terminated_string_missing_null_ignore_error():
    reader = Reader(b"foo bar", errors=Errors.NONE)

    assert reader.read_null_terminated_string() == b"foo bar"


def test_read_fb():
    reader = fixture_reader(fixture("1317.swf"), 1341)
    reader.skip_bits(6)

    assert reader.read_fb(18) == -1.1363677978515625
    assert reader.read_fb(18) == 1.1363677978515625
    assert reader.read_fb(0) == 0.0


def test_read_fb_overflow():
    reader = Reader(b"\x00\x00\x00\x00", 2)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_fb(17)


def test_read_fb_overflow_ignore_error():
    reader = Reader(b"\x00\x00\x00\x00", 2, Errors.NONE)

    assert reader.read_fb(17) == 0.0


def test_read_bool():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(23)

    assert reader.read_bool() is False
    assert reader.read_bool() is False
    assert reader.read_bool() is False
    assert reader.read_bool() is False
    assert reader.read_bool() is True
    assert reader.read_bool() is False
    assert reader.read_bool() is False
    assert reader.read_bool() is False
    assert reader.offset == 24


def test_read_bool_overflow():
    reader = Reader(b"\x00\x00\x00\x00", 1)
    reader.skip_bits(8)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 1, end: 1)")
    ):
        reader.read_bool()


def test_read_bool_overflow_ignore_error():
    reader = Reader(b"\x00\x00\x00\x00", 1, Errors.NONE)
    reader.skip_bits(8)

    assert reader.read_bool() is False


def test_read_sb():
    reader = fixture_reader(fixture("1317.swf"), 34)
    reader.skip_bits(5)

    assert reader.read_sb(7) == -37
    assert reader.read_sb(7) == 37
    assert reader.read_sb(7) == -42
    assert reader.read_sb(7) == 51
    assert reader.read_sb(0) == 0


def test_read_sb_overflow():
    reader = Reader(b"\x00\x00\x00\x00", 2)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_sb(17)


def test_read_sb_overflow_ignore_error():
    reader = Reader(b"\x00\x00\x00\x00", 2, Errors.NONE)

    assert reader.read_sb(17) == 0


def test_read_fixed8():
    reader = fixture_reader(fixture("extractor", "1700", "1700.swf"), 83196)
    assert reader.read_fixed8() == 0.00390625

    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())
    reader.skip_bytes(17)
    assert reader.read_fixed8() == 24.0

    assert Reader(b"\x80\x07").read_fixed8() == 7.5
    assert Reader(b"\x42\xff").read_fixed8() == -0.7421875
    assert Reader(b"\x21\xe3").read_fixed8() == -28.87109375


def test_read_fixed8_overflow():
    reader = Reader(b"\x00\x00\x00\x00", 2)
    reader.skip_bytes(1)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_fixed8()


def test_read_fixed8_overflow_ignore_error():
    reader = Reader(b"\x00\x00\x00\x00", 2, Errors.NONE)
    reader.skip_bytes(1)

    assert reader.read_fixed8() == 0.0


def test_read_fixed():
    reader = fixture_reader(fixture("extractor", "54", "54.swf"), 6861)

    assert reader.read_fixed() == 23.0
    assert reader.read_fixed() == 23.0
    assert reader.read_fixed() == 0.7853851318359375
    assert reader.read_fixed() == 0.0

    assert Reader(b"\x00\x80\x07\x00").read_fixed() == 7.5
    assert Reader(b"\x14\x80\x12\xff").read_fixed() == -237.49969482421875


def test_read_fixed_overflow():
    reader = Reader(b"\x00\x00\x00\x00", 2)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 2")):
        reader.read_fixed()


def test_read_fixed_overflow_ignore_error():
    reader = Reader(b"\x00\x00\x00\x00", 2, Errors.NONE)

    assert reader.read_fixed() == 0.0


def test_read_float16():
    reader = fixture_reader(fixture("extractor", "core", "core.swf"), 103681)

    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 0.0

    reader.skip_bytes(2)
    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 0.0
    assert reader.read_float16() == 1.7255859375

    assert Reader(b"\x00\x00").read_float16() == 0.0
    assert num(Reader(b"\x00\x00").read_float16()) == "0"
    assert Reader(b"\x00\x80").read_float16() == -0.0
    assert num(Reader(b"\x00\x80").read_float16()) == "-0"
    assert Reader(b"\x01\x00").read_float16() == 2.9802322387695312e-8
    assert Reader(b"\x01\x80").read_float16() == -2.9802322387695312e-8
    assert Reader(b"\x00\x04").read_float16() == 3.0517578125e-5
    assert Reader(b"\x00\x3c").read_float16() == 0.5
    assert Reader(b"\x00\x40").read_float16() == 1.0
    assert Reader(b"\x00\xc0").read_float16() == -1.0
    assert Reader(b"\x00\x44").read_float16() == 2.0
    assert Reader(b"\x00\x7c").read_float16() == math.inf
    assert Reader(b"\x00\xfc").read_float16() == -math.inf
    assert math.isnan(Reader(b"\x00\x7e").read_float16())


def test_read_float16_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 1, end: 1)")
    ):
        reader.read_float16()


def test_read_float16_overflow_ignore_error():
    reader = Reader(b"\x12\x00", 1, Errors.NONE)

    assert reader.read_float16() == 5.364418029785156e-7


def test_read_float():
    reader = fixture_reader(fixture("extractor", "62", "62.swf"), 5584)

    expected = [
        1.06,
        0.0,
        0.0,
        0.0,
        -9.109997,
        0.0,
        1.06,
        0.0,
        0.0,
        -9.10997,
        0.0,
        0.0,
        1.06,
        0.0,
        -9.10997,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
    ]

    for value in expected:
        assert reader.read_float() == pytest.approx(value, abs=0.0001)


def test_read_float_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 1")):
        reader.read_float()


def test_read_float_overflow_ignore_error():
    reader = Reader(b"\x00\x00", 1, Errors.NONE)

    assert reader.read_float() == 0.0


def test_read_double():
    reader = fixture_reader(fixture("big.swf"), 106)

    assert reader.read_double() == 1234567890123.1235

    reader.skip_bytes(7)
    assert reader.read_double() == -1234567890123.1235


def test_read_double_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 1")):
        reader.read_double()


def test_read_double_overflow_ignore_error():
    reader = Reader(b"\x00\x00", 1, Errors.NONE)

    assert reader.read_double() == 0.0


def test_read_ui8():
    reader = fixture_reader(fixture("parser", "Examples1.swf"), 4467)

    assert reader.read_ui8() == 255
    assert reader.read_ui8() == 153
    assert reader.read_ui8() == 204
    assert reader.read_ui8() == 255


def test_read_ui8_overflow():
    reader = Reader(b"\x00\x00", 1)
    reader.skip_bytes(1)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 1, end: 1)")
    ):
        reader.read_ui8()


def test_read_ui8_overflow_ignore_error():
    reader = Reader(b"\x00\x42", 1, Errors.NONE)
    reader.skip_bytes(1)

    assert reader.read_ui8() == 0


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x00\x00", 0),
        (b"\x01\x00", 1),
        (b"\xff\xff", -1),
        (b"\xff\x7f", 32767),
        (b"\x00\x80", -32768),
        (b"\x39\x30", 12345),
        (b"\xc7\xcf", -12345),
    ],
)
def test_read_si16(data: bytes, expected: int):
    assert Reader(data).read_si16() == expected


def test_read_si16_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 1, end: 1)")
    ):
        reader.read_si16()


def test_read_si16_overflow_ignore_error():
    reader = Reader(b"\x12\x34", 1, Errors.NONE)

    assert reader.read_si16() == 18


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x00\x00", 0),
        (b"\x01\x00", 1),
        (b"\xff\xff", 65535),
        (b"\xff\x7f", 32767),
        (b"\x00\x80", 32768),
        (b"\x39\x30", 12345),
        (b"\xc7\xcf", 53191),
    ],
)
def test_read_ui16(data: bytes, expected: int):
    assert Reader(data).read_ui16() == expected


def test_read_ui16_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 1, end: 1)")
    ):
        reader.read_ui16()


def test_read_ui16_overflow_ignore_error():
    reader = Reader(b"\x12\x34", 1, Errors.NONE)

    assert reader.read_ui16() == 18


def test_read_si32():
    reader = fixture_reader(fixture("big.swf"), 84)

    assert reader.read_si32() == 1234567890
    reader.skip_bytes(7)
    assert reader.read_si32() == -1234567890


def test_read_si32_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 1")):
        reader.read_si32()


def test_read_si32_overflow_ignore_error():
    reader = Reader(b"\x12\x34", errors=Errors.NONE)

    assert reader.read_si32() == 13330


def test_read_ui32():
    reader = Reader(fixture("parser", "uncompressed.swf").read_bytes())

    reader.skip_bytes(4)
    assert reader.read_ui32() == 180786

    reader.skip_bytes(4014)
    assert reader.read_ui32() == 28698


def test_read_ui32_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 4 bytes from offset 0, end is at 1")):
        reader.read_ui32()


def test_read_ui32_overflow_ignore_error():
    reader = Reader(b"\x12\x34", errors=Errors.NONE)

    assert reader.read_ui32() == 13330


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x00\x00\x00\x00\x00\x00\x00\x00", 0),
        (b"\x01\x00\x00\x00\x00\x00\x00\x00", 1),
        (b"\xff\xff\xff\xff\xff\xff\xff\xff", -1),
        (b"\xff\xff\xff\xff\xff\xff\xff\x7f", 9223372036854775807),
        (b"\x00\x00\x00\x00\x00\x00\x00\x80", -9223372036854775808),
        (b"\xd2\x04\x00\x00\x00\x00\x00\x00", 1234),
    ],
)
def test_read_si64(data: bytes, expected: int):
    assert Reader(data).read_si64() == expected


def test_read_si64_overflow():
    reader = Reader(b"\x00\x00", 1)

    with pytest.raises(OutOfBoundsError, match=re.escape("Cannot read 8 bytes from offset 0, end is at 1")):
        reader.read_si64()


def test_read_si64_overflow_ignore_error():
    reader = Reader(b"\x12\x34", errors=Errors.NONE)

    assert reader.read_si64() == 13330


def test_read_encoded_u32():
    reader = fixture_reader(fixture("139.swf"), 38)

    assert reader.read_encoded_u32() == 1
    assert reader.offset == 39
    assert reader.read_encoded_u32() == 0
    assert reader.offset == 40

    reader.skip_bytes(190)
    assert reader.read_encoded_u32() == 158
    assert reader.offset == 232

    assert Reader(b"\x00").read_encoded_u32() == 0
    assert Reader(b"\x2a").read_encoded_u32() == 42
    assert Reader(b"\x7f").read_encoded_u32() == 127
    assert Reader(b"\x80\x01").read_encoded_u32() == 128
    assert Reader(b"\xff\x01").read_encoded_u32() == 255
    assert Reader(b"\xff\x2a").read_encoded_u32() == 5503
    assert Reader(b"\xff\xff\x01").read_encoded_u32() == 32_767
    assert Reader(b"\x80\x80\x80\x01").read_encoded_u32() == 2_097_152
    assert Reader(b"\x80\x80\x80\x80\x01").read_encoded_u32() == 268_435_456
    assert Reader(b"\xff\xff\xff\xff\x0f").read_encoded_u32() == 4_294_967_295
    assert Reader(b"\xff\xff\xff\xff\x7f").read_encoded_u32() == 34_359_738_367


def test_read_encoded_u32_overflow():
    reader = Reader(b"\x80\x80\x01", 2)

    with pytest.raises(
        OutOfBoundsError, match=re.escape("Trying to access data after the end of the input stream (offset: 2, end: 2)")
    ):
        reader.read_encoded_u32()


def test_read_encoded_u32_overflow_ignore_error():
    reader = Reader(b"\x84\x85\x01", 2, Errors.NONE)

    assert reader.read_encoded_u32() == 644
