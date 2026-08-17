"""
Unit tests for Data Serializer
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
from apx.data import Serializer  # noqa E402


class TestSerializerUInt8(unittest.TestCase):

    def test_pack_uint8_from_int(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(0)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        serializer.set_value(255)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0, 255]))

    def test_pack_uint8_from_int_out_of_range(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-1)
        self.assertEqual(serializer.pack_uint8(),
                         apx_base.Result.VALUE_RANGE_ERROR)
        serializer.set_value(256)
        self.assertEqual(serializer.pack_uint8(),
                         apx_base.Result.VALUE_RANGE_ERROR)

    def test_pack_uint8_with_range_check(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(7)
        self.assertEqual(serializer.check_value_in_range(
            0, 7), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([7]))

    def test_pack_uint8_array(self):
        buffer = bytearray(4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([1, 2, 3, 4])
        self.assertEqual(serializer.pack_uint8(4), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([1, 2, 3, 4]))

    def test_pack_dynamic_uint8_array_with_uint8_size(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([10])
        self.assertEqual(serializer.pack_uint8(
            1, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([1, 10]))
        buffer = bytearray(3)
        serializer.set_write_buffer(buffer)
        serializer.set_value([10, 20])
        self.assertEqual(serializer.pack_uint8(
            2, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([2, 10, 20]))
        max_array_len = 8
        buffer = bytearray(9)
        serializer.set_write_buffer(buffer)
        serializer.set_value([10, 20, 30])
        # Give max array size of 8 but only use 3 array elements
        self.assertEqual(serializer.pack_uint8(
            max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([3, 10, 20, 30, 0, 0, 0, 0, 0]))

    def test_pack_record_with_uint8_elements(self):
        buffer = bytearray(3)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({"Red": 2, "Green": 0x12, "Blue": 0xaa})
        serializer.record_select("Red", True)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Green", False)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Blue", False)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x02, 0x12, 0xaa]))

    def test_pack_record_with_uint8_elements_and_range_check(self):
        buffer = bytearray(3)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({"First": 7, "Second": 3, "Third": 3})
        serializer.record_select("First", True)
        self.assertEqual(serializer.check_value_in_range(
            0, 7), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Second", False)
        self.assertEqual(serializer.check_value_in_range(
            0, 3), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Third", False)
        self.assertEqual(serializer.check_value_in_range(
            0, 3), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([7, 3, 3]))


class TestSerializerUInt16(unittest.TestCase):

    def test_pack_uint16_from_int(self):
        buffer = bytearray(6)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(0)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        serializer.set_value(65535)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        serializer.set_value(0x1234)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0, 0, 0xFF, 0xFF, 0x34, 0x12]))

    def test_pack_uint16_array(self):
        buffer = bytearray(2 * 5)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([0x11a, 0x21b, 0x31c, 0x41d, 0x51e])
        self.assertEqual(serializer.pack_uint16(5), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x1a, 0x01,
                                            0x1b, 0x02,
                                            0x1c, 0x03,
                                            0x1d, 0x04,
                                            0x1e, 0x05]))

    def test_pack_dynamic_uint16_array_with_uint8_size(self):
        buffer = bytearray(1 + 2 * 1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([0x1234])
        self.assertEqual(serializer.pack_uint16(
            1, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([1, 0x34, 0x12]))
        buffer = bytearray(1 + 2 * 2)
        serializer.set_write_buffer(buffer)
        serializer.set_value([0x1234, 0x1234])
        self.assertEqual(serializer.pack_uint16(
            2, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([2, 0x34, 0x12, 0x34, 0x12]))
        max_array_len = 5
        buffer = bytearray(1 + 2 * 5)
        serializer.set_write_buffer(buffer)
        serializer.set_value([10, 20, 30])
        self.assertEqual(serializer.pack_uint16(
            max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([3,
                                            10, 0,
                                            20, 0,
                                            30, 0,
                                            0, 0,
                                            0, 0]))


class TestSerializerUInt32(unittest.TestCase):

    def test_pack_uint32_from_int(self):
        buffer = bytearray(12)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(0)
        self.assertEqual(serializer.pack_uint32(), apx_base.Result.NO_ERROR)
        serializer.set_value(0xFFFFFFFF)
        self.assertEqual(serializer.pack_uint32(), apx_base.Result.NO_ERROR)
        serializer.set_value(0x12345678)
        self.assertEqual(serializer.pack_uint32(), apx_base.Result.NO_ERROR)
        expected = [0, 0, 0, 0,
                    0xFF, 0xFF, 0xFF, 0xFF,
                    0x78, 0x56, 0x34, 0x12]
        self.assertEqual(buffer, bytearray(expected))

    def test_pack_uint32_array(self):
        buffer = bytearray(4 * 2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([100000, 200000])
        self.assertEqual(serializer.pack_uint32(2), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xa0, 0x86, 0x01, 0x00,
                                            0x40, 0x0d, 0x03, 0x00]))

    def test_pack_dynamic_uint32_array_with_uint8_size(self):
        buffer = bytearray(1 + 4 * 1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([0x12345678])
        self.assertEqual(serializer.pack_uint32(
            1, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([1, 0x78, 0x56, 0x34, 0x12]))
        buffer = bytearray(1 + 4 * 2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([0x12345678, 0x12345678])
        self.assertEqual(serializer.pack_uint32(
            2, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray(
            [2, 0x78, 0x56, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12]))
        max_array_len = 5
        buffer = bytearray(1 + 4 * 5)
        serializer.set_write_buffer(buffer)
        serializer.set_value([10, 20, 30])
        self.assertEqual(serializer.pack_uint32(
            max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([3,
                                            10, 0, 0, 0,
                                            20, 0, 0, 0,
                                            30, 0, 0, 0,
                                            0, 0, 0, 0,
                                            0, 0, 0, 0]))


class TestSerializerUInt64(unittest.TestCase):

    def test_pack_uint64_from_int(self):
        buffer = bytearray(16)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(0)
        self.assertEqual(serializer.pack_uint64(), apx_base.Result.NO_ERROR)
        serializer.set_value(18446744073709551615)
        self.assertEqual(serializer.pack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]))

    def test_pack_uint64_array(self):
        buffer = bytearray(16)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([0, 0x0123456789abcdef])
        self.assertEqual(serializer.pack_uint64(2), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                            0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 0x01]))


class TestSerializerInt8(unittest.TestCase):

    def test_pack_int8_from_int(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-128)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        serializer.set_value(127)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x80, 127]))

    def test_pack_int8_from_value_out_of_range_yields_range_error(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(128)
        self.assertEqual(serializer.pack_int8(),
                         apx_base.Result.VALUE_RANGE_ERROR)

    def test_pack_int8_with_range_check(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-1)
        self.assertEqual(serializer.check_value_in_range(-3, 3),
                         apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xFF]))

    def test_pack_uint8_array(self):
        buffer = bytearray(4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([-2, -1, 0, 1])
        self.assertEqual(serializer.pack_int8(4), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xFE, 0xFF, 0, 1]))

    def test_pack_dynamic_int8_array_with_uint8_size(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([-127])
        self.assertEqual(serializer.pack_int8(
            1, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([1, 0x81]))
        max_array_len = 5
        buffer = bytearray(6)
        serializer.set_write_buffer(buffer)
        serializer.set_value([-1, 10, 20])
        # Give max array size of 5 but only use 3 array elements
        self.assertEqual(serializer.pack_int8(
            max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([3, 0xFF, 10, 20, 0, 0]))

    def test_pack_record_with_uint8_elements(self):
        buffer = bytearray(3)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({"First": -50, "Second": -100, "Third": -120})
        serializer.record_select("First", True)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Second", False)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        serializer.record_select("Third", False)
        self.assertEqual(serializer.pack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xCE, 0x9C, 0x88]))


class TestSerializerInt16(unittest.TestCase):

    def test_pack_int16_from_int(self):
        buffer = bytearray(4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-32768)
        self.assertEqual(serializer.pack_int16(), apx_base.Result.NO_ERROR)
        serializer.set_value(32767)
        self.assertEqual(serializer.pack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x00, 0x80, 0xff, 0x7f]))

    def test_pack_int16_from_value_out_of_range_yields_range_error(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(32768)
        self.assertEqual(serializer.pack_int16(),
                         apx_base.Result.VALUE_RANGE_ERROR)

    def test_pack_int16_with_range_check(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-1)
        self.assertEqual(serializer.check_value_in_range(-3, 3),
                         apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xFF, 0xFF]))

    def test_pack_uint16_array(self):
        buffer = bytearray(8)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([-2, -1, 0, 1])
        self.assertEqual(serializer.pack_int16(4), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray(
            [0xFE, 0xFF, 0xFF, 0xFF, 0, 0, 1, 0]))


class TestSerializerInt32(unittest.TestCase):

    def test_pack_int32_from_int(self):
        buffer = bytearray(8)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-2147483648)
        self.assertEqual(serializer.pack_int32(), apx_base.Result.NO_ERROR)
        serializer.set_value(2147483647)
        self.assertEqual(serializer.pack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray(
            [0x00, 0x00, 0x00, 0x80, 0xff, 0xff, 0xff, 0x7f]))

    def test_pack_int32_from_value_out_of_range_yields_range_error(self):
        buffer = bytearray(4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(2147483648)
        self.assertEqual(serializer.pack_int32(),
                         apx_base.Result.VALUE_RANGE_ERROR)

    def test_pack_int32_with_range_check(self):
        buffer = bytearray(4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-1)
        self.assertEqual(serializer.check_value_in_range(-3, 3),
                         apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xFF, 0xFF, 0xFF, 0xFF]))

    def test_pack_uint16_array(self):
        buffer = bytearray(16)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([-2, -1, 0, 1])
        self.assertEqual(serializer.pack_int32(4), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xFE, 0xFF, 0xFF, 0xFF,
                                            0xFF, 0xFF, 0xFF, 0xFF,
                                            0, 0, 0, 0,
                                            1, 0, 0, 0]))


class TestSerializerInt64(unittest.TestCase):

    def test_pack_int64_from_int(self):
        buffer = bytearray(16)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(-9223372036854775808)
        self.assertEqual(serializer.pack_int64(), apx_base.Result.NO_ERROR)
        serializer.set_value(9223372036854775807)
        self.assertEqual(serializer.pack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80,
                                            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f]))

    def test_pack_int64_array(self):
        buffer = bytearray(16)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([-1, 1])
        self.assertEqual(serializer.pack_int64(2), apx_base.Result.NO_ERROR)
        self.assertEqual(buffer, bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                                            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))


class TestSerializerAsciiString(unittest.TestCase):

    def test_pack_char(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("a")
        self.assertEqual(serializer.pack_char(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        self.assertEqual(buffer, bytearray("a", encoding="ASCII"))

    def test_pack_char_string(self):
        buffer = bytearray([0xFF, 0xFF, 0xFF, 0xFF])
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Test")
        self.assertEqual(serializer.pack_char(4), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 4)
        self.assertEqual(buffer, bytearray(b"Test"))

    def test_pack_shorter_char_string(self):
        buffer = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Tst")
        self.assertEqual(serializer.pack_char(6), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 6)
        self.assertEqual(buffer, bytearray(b"Tst\x00\x00\x00"))

    def test_pack_too_large_char_string(self):
        buffer = bytearray([0xFF, 0xFF, 0xFF, 0xFF])
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Short")
        self.assertEqual(serializer.pack_char(4), apx_base.Result.VALUE_LENGTH_ERROR)
        self.assertEqual(serializer.bytes_written(), 0)

    def test_pack_dynamic_char_with_uint8_size(self):
        max_array_len = 10
        buffer = bytearray(1 + max_array_len)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("abc")
        self.assertEqual(serializer.pack_char(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1 + 3)
        self.assertEqual(buffer[:4], bytearray([3]) + bytearray(b"abc"))

    def test_pack_dynamic_char_with_uint8_size_with_embedded_null(self):
        max_array_len = 10
        buffer = bytearray(1 + max_array_len)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("ab\0cd")
        self.assertEqual(serializer.pack_char(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1 + 5)
        self.assertEqual(buffer[:6], bytearray([5]) + bytearray(b"ab\x00cd"))


class TestSerializerChar8String(unittest.TestCase):

    def test_pack_char8_single_ascii(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("a")
        self.assertEqual(serializer.pack_char8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer, bytearray("a", encoding="UTF-8"))

    def test_pack_char8_single_non_ascii_too_large(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("ö")
        # 'ö' is 2 bytes in UTF-8 (0xC3, 0xB6), exceeding single char capacity of 1 byte
        self.assertEqual(serializer.pack_char8(),
                         apx_base.Result.VALUE_LENGTH_ERROR)
        self.assertEqual(serializer.bytes_written(), 0)

    def test_pack_char8_koping_exact_length(self):
        # "Köping" in UTF-8 is 7 bytes (0x4B, 0xC3, 0xB6, 0x70, 0x69, 0x6E, 0x67)
        utf8_bytes = "Köping".encode("utf-8")
        self.assertEqual(len(utf8_bytes), 7)
        buffer = bytearray(len(utf8_bytes))
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Köping")
        self.assertEqual(serializer.pack_char8(7), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 7)
        self.assertEqual(buffer, bytearray(utf8_bytes))

    def test_pack_char8_koping_padded_shorter_string(self):
        # Array capacity 10 with 7-byte UTF-8 string "Köping", padded with 3 null bytes
        buffer = bytearray([0xFF] * 10)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Köping")
        self.assertEqual(serializer.pack_char8(10), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 10)
        expected = bytearray("Köping".encode("utf-8")) + \
            bytearray(b"\x00\x00\x00")
        self.assertEqual(buffer, expected)

    def test_pack_char8_koping_too_large_yields_length_error(self):
        # 6-byte capacity is too small for 7-byte UTF-8 "Köping"
        buffer = bytearray(6)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Köping")
        self.assertEqual(serializer.pack_char8(
            6), apx_base.Result.VALUE_LENGTH_ERROR)
        self.assertEqual(serializer.bytes_written(), 0)

    def test_pack_char8_kopenhamn_exact_length(self):
        # "Köpenhamn" in UTF-8 is 10 bytes
        utf8_bytes = "Köpenhamn".encode("utf-8")
        self.assertEqual(len(utf8_bytes), 10)
        buffer = bytearray(len(utf8_bytes))
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("Köpenhamn")
        self.assertEqual(serializer.pack_char8(10), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 10)
        self.assertEqual(buffer, bytearray(utf8_bytes))


class TestSerializerBool(unittest.TestCase):

    def test_pack_bool_from_bool_value(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(False)
        self.assertEqual(serializer.pack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 0)
        serializer.set_write_buffer(buffer)
        serializer.set_value(True)
        self.assertEqual(serializer.pack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 1)

    def test_pack_bool_from_uint32_value(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(0)
        self.assertEqual(serializer.pack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 0)
        serializer.set_write_buffer(buffer)
        serializer.set_value(1)
        self.assertEqual(serializer.pack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 1)

    def test_pack_bool_array(self):
        buffer = bytearray(3)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([True, False, True])
        self.assertEqual(serializer.pack_bool(3), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 3)
        self.assertEqual(buffer, bytearray([1, 0, 1]))

    def test_pack_dynamic_bool_array_with_uint8_length(self):
        buffer = bytearray(1 + 4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([False, True])
        self.assertEqual(serializer.pack_bool(
            4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 3)
        self.assertEqual(buffer[0], 2)
        self.assertEqual(buffer[1], 0)
        self.assertEqual(buffer[2], 1)

    def test_pack_bool_from_invalid_value_yields_conversion_error(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value("not a bool")
        self.assertEqual(serializer.pack_bool(),
                         apx_base.Result.VALUE_CONVERSION_ERROR)
        self.assertEqual(serializer.bytes_written(), 0)

    def test_pack_bool_array_with_invalid_value_yields_conversion_error(self):
        buffer = bytearray(3)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([True, "invalid", False])
        self.assertEqual(serializer.pack_bool(3),
                         apx_base.Result.VALUE_CONVERSION_ERROR)


class TestSerializerByte(unittest.TestCase):

    def test_pack_single_byte(self):

        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0xAA]))
        self.assertEqual(serializer.pack_byte(1), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 0xAA)

    def test_pack_byte_array(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0x12, 0x34]))
        self.assertEqual(serializer.pack_byte(2), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 2)
        self.assertEqual(buffer[0], 0x12)
        self.assertEqual(buffer[1], 0x34)

    def test_pack_zero_length_byte_array_is_treated_as_length_one(self):
        buffer = bytearray(1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0xAA]))
        self.assertEqual(serializer.pack_byte(0), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1)
        self.assertEqual(buffer[0], 0xAA)

    def test_pack_byte_array_with_inconsistent_length_returns_length_error(self):
        buffer = bytearray(2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0x11]))
        self.assertEqual(serializer.pack_byte(
            2), apx_base.Result.VALUE_LENGTH_ERROR)
        self.assertEqual(serializer.bytes_written(), 0)

    def test_pack_dynamic_byte_array_with_uint8_length(self):
        buffer = bytearray(1 + 4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0x0A]))
        self.assertEqual(serializer.pack_byte(
            4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 2)
        self.assertEqual(buffer[0], 1)
        self.assertEqual(buffer[1], 10)

    def test_pack_dynamic_byte_array_with_uint16_length(self):
        buffer = bytearray(2 + 4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value(bytes([0x0A]))
        self.assertEqual(serializer.pack_byte(
            4, apx_base.SizeType.UINT16), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 3)
        self.assertEqual(buffer[0], 1)
        self.assertEqual(buffer[1], 0)
        self.assertEqual(buffer[2], 10)


class TestSerializerRecord(unittest.TestCase):
    def test_pack_record_inside_record__uint8_uint16__uint16_uint32(self):

        buffer = bytearray(9)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({
            "First": {"Inner1": 0x12, "Inner2": 0x1234},
            "Second": {"Inner3": 0x1234, "Inner4": 0x12345678}
        })
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Inner1", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Inner2", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Inner3", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Inner4", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        self.assertEqual(buffer, bytearray(
            [0x12, 0x34, 0x12, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12]))

    def test_pack_array_of_record_uint16_uint8(self):
        buffer = bytearray(9)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([
            {"Id": 1000, "Value": 1},
            {"Id": 2000, "Value": 0},
            {"Id": 4000, "Value": 1},
        ])
        self.assertEqual(serializer.pack_record(3), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = serializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(serializer.record_select(
            "Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = serializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(serializer.record_select(
            "Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select(
            "Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = serializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertTrue(is_last)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        self.assertEqual(buffer, bytearray([
            0xE8, 0x03, 0x01,
            0xD0, 0x07, 0x00,
            0xA0, 0x0F, 0x01,
        ]))

    def test_pack_dynamic_string_in_record(self):
        # DATA SIGNATURE: {"First"a[10*]"Second"a[10*]}
        buffer = bytearray((1 + 10) * 2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({
            "First": "Hello",
            "Second": "APX",
        })
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), 1 + 10 + 1 + 3)
        self.assertEqual(buffer[0], 5)
        self.assertEqual(buffer[1:6], bytearray(b"Hello"))
        self.assertEqual(buffer[6:11], bytearray([0] * 5))
        self.assertEqual(buffer[11], 3)
        self.assertEqual(buffer[12:15], bytearray(b"APX"))
        self.assertEqual(buffer[15:22], bytearray([0] * 7))

    def test_pack_dynamic_uint16_array_in_record(self):
        # DATA SIGNATURE: {"First"S[5*]"Second"C}
        buffer = bytearray(1 + 2 * 5 + 1)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({
            "First": [1000, 2000],
            "Second": 255,
        })
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint16(5, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        self.assertEqual(buffer[0], 2)
        self.assertEqual(buffer[1:5], bytearray([0xE8, 0x03, 0xD0, 0x07]))
        self.assertEqual(buffer[5:11], bytearray([0] * 6))
        self.assertEqual(buffer[11], 0xFF)

    def test_pack_record_with_dynamic_string_and_status(self):
        # DATA SIGNATURE: {"Name"a[8*]"Status"L}
        buffer = bytearray(1 + 8 + 4)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value({
            "Name": "Hi",
            "Status": 0x12345678,
        })
        self.assertEqual(serializer.pack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Name", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_char(8, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Status", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        self.assertEqual(buffer[0], 2)
        self.assertEqual(buffer[1:3], bytearray(b"Hi"))
        self.assertEqual(buffer[3:9], bytearray([0] * 6))
        self.assertEqual(buffer[9:13], bytearray([0x78, 0x56, 0x34, 0x12]))

    def test_pack_array_of_records_with_dynamic_string(self):
        # DATA SIGNATURE: {"Label"a[4*]"Id"C}[2]
        buffer = bytearray((1 + 4 + 1) * 2)
        serializer = Serializer()
        serializer.set_write_buffer(buffer)
        serializer.set_value([
            {"Label": "Cat", "Id": 10},
            {"Label": "A", "Id": 20},
        ])
        self.assertEqual(serializer.pack_record(2), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Label", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_char(4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Id", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = serializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(serializer.record_select("Label", True), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_char(4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_select("Id", False), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.pack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(serializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = serializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertTrue(is_last)
        self.assertEqual(serializer.bytes_written(), len(buffer))
        expected = bytearray([
            3, ord('C'), ord('a'), ord('t'), 0, 10,
            1, ord('A'), 0, 0, 0, 20
        ])
        self.assertEqual(buffer, expected)
