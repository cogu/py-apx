"""
Unit tests for DataElement model
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base
import apx.model as apx_model


class TestDataElements(unittest.TestCase):

    def test_create_uint8(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(data_element.is_array)
        self.assertFalse(data_element.has_limits)

    def test_create_uint8_with_limits(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
        data_element.set_limits(0, 7)
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(data_element.is_array)
        self.assertTrue(data_element.has_limits)

    def test_create_uint8_array(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
        data_element.array_len = 10
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.is_array)
        self.assertFalse(data_element.has_limits)

    def test_create_record_uint8_uint16(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.RECORD)
        data_element.elements.append(apx_model.DataElement(apx_base.TypeCode.UINT8))
        data_element.elements.append(apx_model.DataElement(apx_base.TypeCode.UINT16))
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(data_element.is_array)
        self.assertFalse(data_element.has_limits)
        child_elem = data_element.elements[0]
        self.assertEqual(child_elem.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(child_elem.is_array)
        self.assertFalse(child_elem.has_limits)
        child_elem = data_element.elements[1]
        self.assertEqual(child_elem.type_code, apx_base.TypeCode.UINT16)
        self.assertFalse(child_elem.is_array)
        self.assertFalse(child_elem.has_limits)

    def test_derive_proper_init_value_uint8(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
        result, derived_init_value = data_element.derive_proper_init_value(7)
        self.assertEqual(result, apx_base.NO_ERROR)
        self.assertEqual(derived_init_value, 7)

    def test_derive_proper_init_value_uint8_array(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
        data_element.array_len = 3
        result, derived_init_value = data_element.derive_proper_init_value([3, 7, 15])
        self.assertEqual(result, apx_base.NO_ERROR)
        self.assertEqual(derived_init_value, [3, 7, 15])

    def test_derive_proper_init_value_char_array(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.CHAR)
        data_element.array_len = 3
        result, derived_init_value = data_element.derive_proper_init_value("init")
        self.assertEqual(result, apx_base.NO_ERROR)
        self.assertEqual(derived_init_value, "init")

    def test_derive_proper_init_value_char_array_invalid_ascii(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.CHAR)
        data_element.array_len = 3
        result, derived_init_value = data_element.derive_proper_init_value("café")
        self.assertEqual(result, apx_base.INIT_VALUE_ERROR)
        self.assertIsNone(derived_init_value)

    def test_derive_proper_init_value_char8_array_valid_utf8(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.CHAR8)
        data_element.array_len = 3
        result, derived_init_value = data_element.derive_proper_init_value("café")
        self.assertEqual(result, apx_base.NO_ERROR)
        self.assertEqual(derived_init_value, "café")

    def test_derive_proper_init_value_char8_array_invalid_utf8(self):
        data_element = apx_model.DataElement(apx_base.TypeCode.CHAR8)
        data_element.array_len = 3
        result, derived_init_value = data_element.derive_proper_init_value("\ud800")
        self.assertEqual(result, apx_base.INIT_VALUE_ERROR)
        self.assertIsNone(derived_init_value)


if __name__ == '__main__':
    unittest.main()
