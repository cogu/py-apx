"""
Unit tests for signature parser
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
import apx.model as apx_model  # noqa E402
from apx.parser import SignatureParser  # noqa E402


class TestSignatureParser(unittest.TestCase):

    def test_parse_uint8(self):
        parser = SignatureParser()
        result = parser.parse_signature('C')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_uint8_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('C(0,3)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 3)

    def test_parse_uint8_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('C[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)

    def test_parse_uint8_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('C(0,7)[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 7)

    def test_parse_uint16(self):
        parser = SignatureParser()
        result = parser.parse_signature('S')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT16)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_uint16_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('S(0,1023)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT16)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 1023)

    def test_parse_uint16_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('S[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT16)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)

    def test_parse_uint16_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('S(0, 1023)[ 8 ]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT16)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 1023)

    def test_parse_uint32(self):
        parser = SignatureParser()
        result = parser.parse_signature('L')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT32)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_uint32_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('L(0, 99999)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()

        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT32)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 99999)

    def test_parse_uint32_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('L[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT32)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)

    def test_parse_uint32_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('L(0, 99999)[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT32)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 99999)

    def test_parse_uint64(self):
        parser = SignatureParser()
        result = parser.parse_signature('Q')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT64)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_uint64_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('Q(0 , 0x100000000)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT64)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 0x100000000)

    def test_parse_uint64_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('Q[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT64)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)

    def test_parse_uint64_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('Q(0, 0x100000000)[8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT64)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 0x100000000)

    def test_parse_int8(self):
        parser = SignatureParser()
        result = parser.parse_signature('c')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT8)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_int8_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('c(-10,10)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT8)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -10)
        self.assertEqual(upper_limit, 10)

    def test_parse_int8_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('c[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT8)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int8_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('c(-10, 10)[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT8)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -10)
        self.assertEqual(upper_limit, 10)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int16(self):
        parser = SignatureParser()
        result = parser.parse_signature('s')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT16)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_int16_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('s(-1000,1000)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT16)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -1000)
        self.assertEqual(upper_limit, 1000)

    def test_parse_int16_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('s[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT16)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int16_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('s(-1000, 1000)[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT16)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -1000)
        self.assertEqual(upper_limit, 1000)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int32(self):
        parser = SignatureParser()
        result = parser.parse_signature('l')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT32)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_int32_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('l(-100000,100000)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT32)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -100000)
        self.assertEqual(upper_limit, 100000)

    def test_parse_int32_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('l[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT32)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int32_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('l(-100000, 100000)[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT32)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -100000)
        self.assertEqual(upper_limit, 100000)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int64(self):
        parser = SignatureParser()
        result = parser.parse_signature('q')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT64)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_int64_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('q(-100000,100000)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT64)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -100000)
        self.assertEqual(upper_limit, 100000)

    def test_parse_int64_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('q[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT64)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_int64_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('q(-100000, 100000)[6]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.INT64)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, -100000)
        self.assertEqual(upper_limit, 100000)
        self.assertEqual(data_element.array_len, 6)

    def test_parse_byte(self):
        parser = SignatureParser()
        result = parser.parse_signature('B')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_byte_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('B(0, 3)')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertTrue(data_element.has_limits)
        self.assertFalse(data_element.is_array)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 3)

    def test_parse_byte_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('B[10]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 10)

    def test_parse_byte_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('B(0, 7)[10]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 10)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 7)

    def test_parse_dynamic_byte_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('B[10*]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertTrue(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 10)

    def test_parse_dynamic_byte_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('B(0,7)[10*]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.BYTE)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertTrue(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 10)
        lower_limit, upper_limit = data_element.get_limits()
        self.assertEqual(lower_limit, 0)
        self.assertEqual(upper_limit, 7)

    def test_parse_char(self):
        parser = SignatureParser()
        result = parser.parse_signature('a')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_char8(self):
        parser = SignatureParser()
        result = parser.parse_signature('A')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR8)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_char16(self):
        parser = SignatureParser()
        result = parser.parse_signature('u')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR16)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_char32(self):
        parser = SignatureParser()
        result = parser.parse_signature('U')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR32)
        self.assertFalse(data_element.has_limits)
        self.assertFalse(data_element.is_array)

    def test_parse_char_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('a[32]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 32)

    def test_parse_dynamic_char_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('a[256*]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertTrue(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 256)

    def test_parse_char8_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('A[32]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR8)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 32)

    def test_parse_dynamic_char8_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('A[256*]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR8)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertTrue(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 256)

    def test_parse_char16_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('u[32]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR16)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 32)

    def test_parse_char32_array(self):
        parser = SignatureParser()
        result = parser.parse_signature('U[32]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertIsInstance(data_element, apx_model.DataElement)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR32)
        self.assertFalse(data_element.has_limits)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 32)

    def test_parse_char_array_with_limits(self):
        parser = SignatureParser()
        result = parser.parse_signature('a(0,127)[20]')
        self.assertEqual(result, apx_base.Result.PARSE_ERROR)
        # Parsing should stop on '('-character. Limits is not allowed on character types.
        self.assertEqual(1, parser.read_position)

    def test_parse_record_u8_u8_u8(self):
        parser = SignatureParser()
        result = parser.parse_signature('{\"ID\"C(0,127)\"Stat\"C(0,3)\"Type\"C(0,7)}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(data_element.elements), 3)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(child_element.name, "ID")
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(child_element.name, "Stat")
        child_element = data_element.elements[2]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(child_element.name, "Type")

    def test_parse_record_u8u8_u8u8(self):
        parser = SignatureParser()
        signature = '{\"Notification1\"{\"ID1\"C(0,127)\"Stat1\"C(0,3)}\"Notification2\"{\"ID2\"C(0,127)\"Stat2\"C(0,3)}}' # noqa E501
        result = parser.parse_signature(signature)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(data_element.elements), 2)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(child_element.name, "Notification1")
        grand_child = child_element.elements[0]
        self.assertEqual(grand_child.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(grand_child.name, "ID1")
        grand_child = child_element.elements[1]
        self.assertEqual(grand_child.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(grand_child.name, "Stat1")
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(child_element.name, "Notification2")
        grand_child = child_element.elements[0]
        self.assertEqual(grand_child.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(grand_child.name, "ID2")
        grand_child = child_element.elements[1]
        self.assertEqual(grand_child.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(grand_child.name, "Stat2")

    def test_parse_record_string_u16(self):
        parser = SignatureParser()
        result = parser.parse_signature('{\"Name\"a[32]\"ID\"S}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(data_element.elements), 2)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.CHAR)
        self.assertEqual(child_element.name, "Name")
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT16)
        self.assertEqual(child_element.name, "ID")

    def test_parse_error_in_record(self):
        parser = SignatureParser()
        result = parser.parse_signature('{{\"ID\"C(0,127)\"Stat\"C(0,3)\"Type\"C(0,7)}')
        self.assertEqual(result, apx_base.Result.PARSE_ERROR)
        self.assertEqual(parser.read_position, 1)

    def test_parse_type_reference_by_id(self):
        parser = SignatureParser()
        result = parser.parse_signature('T[0]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_ID)
        self.assertFalse(data_element.is_array)
        self.assertEqual(data_element.typeref, 0)

    def test_parse_array_of_type_reference_by_id(self):
        parser = SignatureParser()
        result = parser.parse_signature('T[2][8]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_ID)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.is_dynamic_array)
        self.assertEqual(data_element.array_len, 8)
        self.assertEqual(data_element.typeref, 2)

    def test_parse_type_reference_by_name(self):
        parser = SignatureParser()
        result = parser.parse_signature('T["TypeName"]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_NAME)
        self.assertFalse(data_element.is_array)
        self.assertEqual(data_element.typeref, "TypeName")

    def test_parse_type_reference_by_id_inside_record(self):
        parser = SignatureParser()
        result = parser.parse_signature('{"First"T[0]"Second"T[1]}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(data_element.is_array)
        self.assertEqual(len(data_element.elements), 2)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_ID)
        self.assertEqual(child_element.name, "First")
        self.assertFalse(child_element.is_array)
        self.assertEqual(child_element.typeref, 0)
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_ID)
        self.assertEqual(child_element.name, "Second")
        self.assertFalse(child_element.is_array)
        self.assertEqual(child_element.typeref, 1)

    def test_parse_type_reference_by_name_inside_record(self):
        parser = SignatureParser()
        result = parser.parse_signature('{"First"T["Type1"]"Second"T["Type2"]}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(data_element.is_array)
        self.assertEqual(len(data_element.elements), 2)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_NAME)
        self.assertEqual(child_element.name, "First")
        self.assertFalse(child_element.is_array)
        self.assertEqual(child_element.typeref, "Type1")
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_NAME)
        self.assertEqual(child_element.name, "Second")
        self.assertFalse(child_element.is_array)
        self.assertEqual(child_element.typeref, "Type2")

    def test_parse_dynamic_array_of_record(self):
        parser = SignatureParser()
        result = parser.parse_signature('{"Id"S"Status"b}[50*]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        data_element = parser.take_data_element()
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertTrue(data_element.is_array)
        self.assertTrue(data_element.is_dynamic_array)
        self.assertTrue(data_element.array_len, 50)
        self.assertEqual(len(data_element.elements), 2)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT16)
        self.assertEqual(child_element.name, "Id")
        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.BOOL)
        self.assertEqual(child_element.name, "Status")
