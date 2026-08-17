"""
Unit tests for Data Deserializer
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
import struct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base # noqa E402
from apx.data import Deserializer # noqa E402


class TestDeserializerUInt8(unittest.TestCase):

    def test_unpack_uint8(self):
        buffer = bytearray([0, 255])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 1)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.value(), 255)

    def test_range_check_uint8(self):
        buffer = bytearray([7, 8])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 1)
        self.assertEqual(deserializer.check_value_range(0, 7), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.check_value_range(0, 7), apx_base.Result.VALUE_RANGE_ERROR)

    def test_unpack_uint8_array(self):
        values = [0x00, 0x12, 0xff]
        buffer = bytearray(values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(len(values)), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_uint8_array_with_too_short_read_buffer(self):
        values = [0x00, 0x12, 0xff]
        buffer = bytearray([0x00, 0x12, 0xff])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(len(values) + 1), apx_base.Result.BUFFER_BOUNDARY_ERROR)
        self.assertEqual(deserializer.bytes_read(), 0)

    def test_unpack_uint8_array_with_range_check(self):
        values = [0x07, 0x03, 0x7]
        buffer = bytearray(values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(len(values)), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)
        self.assertEqual(deserializer.check_value_range(0, 7), apx_base.Result.NO_ERROR)

    def test_unpack_uint8_dynamic_array_with_uint8_size(self):
        current_array_len = 2
        max_array_len = 3
        values = [1, 2]
        buffer = struct.pack("<B2B", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_uint8_dynamic_array_with_uint16_size(self):
        current_array_len = 3
        max_array_len = 1024
        values = [3, 4, 5]
        buffer = struct.pack("<H3B", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(max_array_len, apx_base.SizeType.UINT16), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_uint8_dynamic_array_with_uint32_size(self):
        current_array_len = 4
        max_array_len = 80000
        values = [6, 7, 8, 9]
        buffer = struct.pack("<L4B", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint8(max_array_len, apx_base.SizeType.UINT32), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_uint8_dynamic_array_with_uint8_size_and_range_check(self):
        current_array_len = 2
        max_array_len = 3
        values1 = [7, 7]
        buffer1 = struct.pack("<B2B", current_array_len, *values1)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer1)
        self.assertEqual(deserializer.unpack_uint8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer1))
        self.assertEqual(deserializer.value(), values1)
        self.assertEqual(deserializer.check_value_range(0, 7), apx_base.Result.NO_ERROR)
        values2 = [7, 8]
        buffer2 = struct.pack("<B2B", current_array_len, *values2)
        deserializer.set_read_buffer(buffer2)
        self.assertEqual(deserializer.unpack_uint8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer2))
        self.assertEqual(deserializer.value(), values2)
        self.assertEqual(deserializer.check_value_range(0, 7), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerUInt16(unittest.TestCase):

    def test_unpack_uint16(self):
        buffer = bytearray([0, 0, 0x34, 0x12, 0xff, 0xff])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.value(), 0x1234)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 6)
        self.assertEqual(deserializer.value(), 0xffff)

    def test_range_check_uint16(self):
        buffer = struct.pack("<2H", 10000, 10000 + 1)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.check_value_range(0, 10000), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.check_value_range(0, 10000), apx_base.Result.VALUE_RANGE_ERROR)

    def test_unpack_uint16_dynamic_array_with_uint8_size(self):
        current_array_len = 3
        max_array_len = 3
        values = [0, 1000, 10000]
        buffer = struct.pack("<B3H", current_array_len, 0, 1000, 10000)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint16(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)


class TestDeserializerUInt32(unittest.TestCase):

    def test_unpack_uint32(self):
        buffer = bytearray([0x00, 0x00, 0x00, 0x00,
                            0x78, 0x56, 0x34, 0x12,
                            0xff, 0xff, 0xff, 0xff])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.value(), 0x12345678)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 12)
        self.assertEqual(deserializer.value(), 0xffffffff)

    def test_range_check_uint32(self):
        buffer = struct.pack("<2L", 100000, 100000 + 1)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.check_value_range(0, 100000), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.check_value_range(0, 100000), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerUInt64(unittest.TestCase):

    def test_unpack_uint64(self):
        buffer = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0xef, 0xcd, 0xab, 0x89, 0x67, 0x45, 0x23, 0x01,
                            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.value(), 0x0123456789abcdef)
        self.assertEqual(deserializer.unpack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 24)
        self.assertEqual(deserializer.value(), 2 ** 64 - 1)

    def test_range_check_uint64(self):
        buffer = struct.pack("<2Q", 25 * 10**9, 25 * 10**9 + 1)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.check_value_range(0, 25000000000), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.check_value_range(0, 25000000000), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerInt8(unittest.TestCase):

    def test_unpack_int8(self):
        buffer = bytearray([0x80, 0xff, 0, 0x7f])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 1)
        self.assertEqual(deserializer.value(), -128)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.value(), -1)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 3)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.value(), 127)

    def test_range_check_int8(self):
        buffer = struct.pack("<4b", -4, -3, 3, 4)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        lower_limit, upper_limit = -3, 3
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 1)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 3)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)

    def test_unpack_int8_dynamic_array_with_uint8_size(self):
        current_array_len = 2
        max_array_len = 3
        values = [-1, -2]
        buffer = struct.pack("<B2b", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_int8_dynamic_array_with_uint16_size(self):
        current_array_len = 3
        max_array_len = 1024
        values = [-3, -4, -5]
        buffer = struct.pack("<H3b", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int8(max_array_len, apx_base.SizeType.UINT16), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)

    def test_unpack_int8_dynamic_array_with_uint32_size(self):
        current_array_len = 4
        max_array_len = 80000
        values = [-6, -7, -8, -9]
        buffer = struct.pack("<L4b", current_array_len, *values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int8(max_array_len, apx_base.SizeType.UINT32), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), values)


class TestDeserializerInt16(unittest.TestCase):

    def test_unpack_int16(self):
        buffer = bytearray([0x00, 0x80,
                            0xff, 0xff,
                            0x00, 0x00,
                            0xff, 0x7f,
                            0xff, 0xff])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.value(), -32768)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.value(), -1)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 6)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.value(), 32767)

    def test_range_check_int16(self):
        buffer = struct.pack("<4h", -401, -400, 400, 401)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        lower_limit, upper_limit = -400, 400
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 2)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 6)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerInt32(unittest.TestCase):

    def test_unpack_int32(self):
        buffer = bytearray([0x00, 0x00, 0x00, 0x80,
                            0xff, 0xff, 0xff, 0xff,
                            0x00, 0x00, 0x00, 0x00,
                            0xff, 0xff, 0xff, 0x7f])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.value(), -2 ** 31)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.value(), -1)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 12)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.value(), 2 ** 31 - 1)

    def test_range_check_int32(self):
        buffer = struct.pack("<4l", -40001, -40000, 40000, 40001)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        lower_limit, upper_limit = -40000, 40000
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 4)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 12)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerInt64(unittest.TestCase):

    def test_unpack_int64(self):
        buffer = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80,
                            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.value(), -2 ** 63)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.value(), -1)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 24)
        self.assertEqual(deserializer.value(), 0)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 32)
        self.assertEqual(deserializer.value(), 2 ** 63 - 1)

    def test_range_check_int64(self):
        buffer = struct.pack("<4q", -4000001, -4000000, 4000000, 4000001)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        lower_limit, upper_limit = -4000000, 4000000
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 8)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 16)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 24)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_int64(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 32)
        self.assertEqual(deserializer.check_value_range(lower_limit, upper_limit), apx_base.Result.VALUE_RANGE_ERROR)


class TestDeserializerAsciiString(unittest.TestCase):

    def test_unpack_char(self):
        value = "a"
        buffer = bytearray(value, encoding="ASCII")
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), value)

    def test_unpack_char_with_trailing_nulls(self):
        current_array_len = 8
        buffer = bytearray([ord(x) for x in "abcd"] + [0, 0, 0, 0])
        self.assertEqual(len(buffer), current_array_len)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char(current_array_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "abcd")

    def test_unpack_filled_char_array(self):
        current_array_len = 8
        buffer = bytearray([ord(x) for x in "abcdefgh"])
        self.assertEqual(len(buffer), current_array_len)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char(current_array_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "abcdefgh")

    def test_unpack_dynamic_char_with_uint8_size(self):
        current_array_len = 3
        max_array_len = 10
        buffer = bytearray([current_array_len] + [ord(x) for x in "abc"])
        self.assertEqual(len(buffer), current_array_len + apx_base.UINT8_SIZE)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "abc")

    def test_unpack_dynamic_char_with_uint8_size_with_embedded_null(self):
        current_array_len = 5
        max_array_len = 10
        buffer = bytearray([current_array_len] + [ord(x) for x in "ab\0cd"])
        self.assertEqual(len(buffer), current_array_len + apx_base.UINT8_SIZE)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "ab\0cd")


class TestDeserializerChar8String(unittest.TestCase):

    def test_unpack_char8_single_ascii(self):
        buffer = bytearray("a", encoding="UTF-8")
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), 1)
        self.assertEqual(deserializer.value(), "a")

    def test_unpack_char8_string_koping(self):
        buffer = bytearray("Köping", encoding="UTF-8")
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(len(buffer)), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "Köping")

    def test_unpack_char8_string_koping_with_padding(self):
        buffer = bytearray("Köping", encoding="UTF-8") + bytearray(b"\x00\x00\x00")
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(len(buffer)), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "Köping")

    def test_unpack_char8_string_kopenhamn(self):
        buffer = bytearray("Köpenhamn", encoding="UTF-8")
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(len(buffer)), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "Köpenhamn")

    def test_unpack_dynamic_char8_with_uint8_size(self):
        utf8_bytes = "Köping".encode("utf-8")
        current_array_len = len(utf8_bytes)
        max_array_len = 10
        buffer = bytearray([current_array_len]) + bytearray(utf8_bytes)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "Köping")

    def test_unpack_dynamic_char8_with_uint8_size_with_embedded_null(self):
        utf8_bytes = "Köp\0ing".encode("utf-8")
        current_array_len = len(utf8_bytes)
        max_array_len = 16
        buffer = bytearray([current_array_len]) + bytearray(utf8_bytes)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_char8(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), "Köp\0ing")


class TestDeserializerBoolean(unittest.TestCase):

    def test_unpack_bool(self):
        buffer = bytearray([1])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), True)

    def test_unpack_bool_array(self):
        array_len = 4
        buffer = bytearray([0, 1, 1, 0])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_bool(array_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), [False, True, True, False])

    def test_unpack_dynamic_boolean_array(self):
        current_array_len = 3
        max_array_len = 8
        buffer = bytearray([current_array_len, 1, 1, 0])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_bool(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), [True, True, False])


class TestDeserializerByte(unittest.TestCase):

    def test_unpack_byte(self):
        values = [0xba]
        buffer = bytes(values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_byte(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), bytes(values))

    def test_unpack_byte_array(self):
        values = [0xa, 0xb, 0xc, 0xd]
        array_len = len(values)
        buffer = bytes(values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_byte(array_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), bytes(values))

    def test_unpack_dynamic_byte_array(self):
        values = [0xb, 0xc, 0xd, 0, 0, 0, 0, 0]
        current_array_len = 3
        max_array_len = 8
        buffer = bytearray([current_array_len] + values)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_byte(max_array_len, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), apx_base.UINT8_SIZE * (1 + current_array_len))
        self.assertEqual(deserializer.value(), bytes([0xb, 0xc, 0xd]))


class TestDeserializerRecord(unittest.TestCase):

    def test_unpack_record_uint8_uint8(self):
        buffer = bytes([0x3, 0x7])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": 3, "Second": 7})

    def test_unpack_record_uint8_array_uint16(self):
        array_len = 3
        buffer = bytes([0x1, 0x2, 0x3, 0x34, 0x12])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(array_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": [1, 2, 3], "Second": 0x1234})

    def test_unpack_record_string_string_bool(self):
        str1_len = 5
        str2_len = 5
        buffer = bytes("Hello", encoding="ASCII") + bytes("World", encoding="ASCII") + bytes([0x01])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(str1_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(str2_len), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Third", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": "Hello",
                                                "Second": "World",
                                                "Third": True})

    def test_unpack_record_inside_record_u8_u16__u16_u32(self):
        buffer = bytes([0x12, 0x34, 0x12, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Inner1", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Inner2", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Inner3", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Inner4", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {
            "First": {"Inner1": 0x12, "Inner2": 0x1234},
            "Second": {"Inner3": 0x1234, "Inner4": 0x12345678}
        })

    def test_unpack_array_of_record_u16_u8(self):
        array_length = 3
        buffer = bytes([
            0xE8, 0x03, 0x01,
            0xd0, 0x07, 0x00,
            0xA0, 0x0F, 0x01,
        ])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(array_length), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = deserializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(deserializer.record_select("Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = deserializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(deserializer.record_select("Id", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Value", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = deserializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertTrue(is_last)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), [
            {"Id": 1000, "Value": 1},
            {"Id": 2000, "Value": 0},
            {"Id": 4000, "Value": 1},
        ])

    def test_unpack_record_dynamic_string_in_record(self):
        # DATA SIGNATURE: {"First"a[10*]"Second"a[10*]}
        buffer = bytes([5]) + b"Hello" + bytes([0xee] * 5) + bytes([3]) + b"APX" + bytes([0xee] * 7)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.value(), {"First": "Hello", "Second": "APX"})

    def test_unpack_record_dynstring_u32array(self):
        # DATA SIGNATURE: {"First"a[10*]"Second"L[2]}
        buffer = bytes([5]) + b"Data1" + bytes([0xee] * 5) + struct.pack("<2L", 0, 0x12345678)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint32(2), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": "Data1", "Second": [0, 0x12345678]})

    def test_unpack_record_dynamic_uint16_array(self):
        # DATA SIGNATURE: {"First"S[5*]"Second"C}
        buffer = bytes([2]) + struct.pack("<2H", 1000, 2000) + bytes([0xee] * 6) + bytes([0xFF])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint16(5, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": [1000, 2000], "Second": 255})

    def test_unpack_record_bool_dynstring(self):
        # DATA SIGNATURE: {"First"b"Second"a[10*]}
        buffer = bytes([0x01, 4]) + b"Data"
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("First", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_bool(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Second", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(10, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"First": True, "Second": "Data"})

    def test_unpack_array_of_records_with_dynamic_string(self):
        # DATA SIGNATURE: {"Label"a[4*]"Id"C}[2]
        buffer = bytes([3]) + b"Cat" + bytes([0xee]) + bytes([10]) + bytes([1]) + b"A" + bytes([0xee] * 3) + bytes([20])
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(2), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Label", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Id", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = deserializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertFalse(is_last)
        self.assertEqual(deserializer.record_select("Label", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(4, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Id", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint8(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        rc, is_last = deserializer.array_next()
        self.assertEqual(rc, apx_base.Result.NO_ERROR)
        self.assertTrue(is_last)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), [
            {"Label": "Cat", "Id": 10},
            {"Label": "A", "Id": 20},
        ])

    def test_unpack_record_with_empty_dynamic_string(self):
        # DATA SIGNATURE: {"Name"a[8*]"Status"L}
        buffer = bytes([0]) + bytes([0xee] * 8) + struct.pack("<L", 0x12345678)
        deserializer = Deserializer()
        deserializer.set_read_buffer(buffer)
        self.assertEqual(deserializer.unpack_record(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Name", True), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_char(8, apx_base.SizeType.UINT8), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_select("Status", False), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.unpack_uint32(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.record_end(), apx_base.Result.NO_ERROR)
        self.assertEqual(deserializer.bytes_read(), len(buffer))
        self.assertEqual(deserializer.value(), {"Name": "", "Status": 0x12345678})
