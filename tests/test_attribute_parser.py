import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
import apx.model as apx_model  # noqa E402
from apx.parser import AttributeParser  # noqa E402


class TestAttributeParser(unittest.TestCase):

    # Port Attribute Tests
    def test_parse_empty_attribute_string(self):
        parser = AttributeParser()
        result, dummy = parser.parse_port_attributes('')
        self.assertEqual(result, apx_base.Result.NO_ERROR)

    def test_parse_init_value_zero(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=0')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, 0)

    def test_parse_init_value_minus_one(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=-')
        self.assertEqual(result, apx_base.Result.PARSE_ERROR)
        result, attr = parser.parse_port_attributes('=-1')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, -1)

    def test_parse_init_value_uint32_max(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=0xffffffff')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, 0xffffffff)
        result, attr = parser.parse_port_attributes('=0xFFFFFFFF')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, 0xffffffff)

    def test_parse_init_value_int32_max(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=0x7fffffff')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, 0x7fffffff)
        result, attr = parser.parse_port_attributes('=2147483647')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, 0x7fffffff)

    def test_parse_init_value_int32_min(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=-0x7fffffff')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, -0x7fffffff)
        result, attr = parser.parse_port_attributes('=-2147483647')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, -2147483647)

    def test_parse_init_value_int32_list(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('={3, 4}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertIsInstance(attr.init_value, list)
        self.assertEqual(len(attr.init_value), 2)
        self.assertEqual(attr.init_value[0], 3)
        self.assertEqual(attr.init_value[1], 4)

    def test_parse_init_value_int32_list_list(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('={ {1, 2}, {3,4} }')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertIsInstance(attr.init_value, list)
        self.assertEqual(len(attr.init_value), 2)
        self.assertIsInstance(attr.init_value[0], list)
        self.assertEqual(attr.init_value[0], [1, 2])
        self.assertIsInstance(attr.init_value[1], list)
        self.assertEqual(attr.init_value[1], [3, 4])

    def test_parse_init_value_empty_initializer(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('={}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertIsInstance(attr.init_value, list)
        self.assertEqual(len(attr.init_value), 0)

    def test_parse_init_value_empty_initializer_in_record(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('={3, {}}')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertIsInstance(attr.init_value, list)
        self.assertEqual(len(attr.init_value), 2)
        self.assertEqual(attr.init_value[0], 3)
        self.assertIsInstance(attr.init_value[1], list)
        self.assertEqual(attr.init_value[1], [])

    def test_parse_init_value_empty_string(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('=""')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, "")

    def test_parse_init_value_utf8_string(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('="\u00c4\u00c5\u00d6"')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertEqual(attr.init_value, "\u00c4\u00c5\u00d6")

    def test_parse_parameter_attribute(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('P')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertFalse(attr.has_init_value)
        self.assertTrue(attr.is_parameter)

    def test_parse_queue_length(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('Q[4]')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertFalse(attr.has_init_value)
        self.assertEqual(attr.queue_length, 4)

    def test_parse_combined_port_attributes(self):
        parser = AttributeParser()
        result, attr = parser.parse_port_attributes('={7, ""}, P')
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertTrue(attr.has_init_value)
        self.assertTrue(attr.is_parameter)

# Type Attribute Tests

    def test_traditional_value_table(self):
        parser = AttributeParser()
        attr_string = 'VT("OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 0)
        self.assertEqual(computation.upper_limit, 3)
        self.assertEqual(len(computation.values), 4)
        self.assertEqual(computation.values[0], "OnOff_Off")
        self.assertEqual(computation.values[1], "OnOff_On")
        self.assertEqual(computation.values[2], "OnOff_Error")
        self.assertEqual(computation.values[3], "OnOff_NotAvailable")

    def test_value_table_with_offset(self):
        parser = AttributeParser()
        attr_string = 'VT(4, "OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 4)
        self.assertEqual(computation.upper_limit, 7)
        self.assertEqual(len(computation.values), 4)

    def test_value_table_with_negative_offset(self):
        parser = AttributeParser()
        attr_string = 'VT(-3, "OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, -3)
        self.assertEqual(computation.upper_limit, 0)
        self.assertEqual(len(computation.values), 4)

    def test_value_table_with_negative_offset_explicit(self):
        parser = AttributeParser()
        attr_string = 'VT(-3, 0, "OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, -3)
        self.assertEqual(computation.upper_limit, 0)
        self.assertEqual(len(computation.values), 4)

    def test_value_single_table_range(self):
        parser = AttributeParser()
        attr_string = 'VT(251, 254, "Error")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 251)
        self.assertEqual(computation.upper_limit, 254)
        self.assertEqual(len(computation.values), 1)
        self.assertEqual(computation.values[0], "Error")

    def test_value_ranges(self):
        parser = AttributeParser()
        attr_string = 'VT(251, 254, "Error"), VT(255, "NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 2)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 251)
        self.assertEqual(computation.upper_limit, 254)
        self.assertEqual(len(computation.values), 1)
        self.assertEqual(computation.values[0], "Error")
        computation = attr.computations[1]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 255)
        self.assertEqual(computation.upper_limit, 255)
        self.assertEqual(len(computation.values), 1)
        self.assertEqual(computation.values[0], "NotAvailable")

    def test_rational_scaling_vehicle_speed(self):
        parser = AttributeParser()
        attr_string = 'RS(0,65280,0,1,64,"km/h")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.RationalScaling)
        self.assertEqual(computation.lower_limit, 0)
        self.assertEqual(computation.upper_limit, 65280)
        self.assertEqual(computation.offset, 0.0)
        self.assertEqual(computation.numerator, 1)
        self.assertEqual(computation.denominator, 64)
        self.assertEqual(computation.unit, "km/h")

    def test_combined_type_attributes(self):
        parser = AttributeParser()
        attr_string = 'RS(0, 0xFDFF, 0, 1, 64, "km/h"), VT(0xFE00, 0xFEFF, "Error"), VT(0xFF00, 0xFFFF, "NotAvailable")'
        result, attr = parser.parse_type_attributes(attr_string)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(attr, apx_model.TypeAttributes)
        self.assertEqual(len(attr.computations), 3)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.RationalScaling)
        self.assertEqual(computation.lower_limit, 0)
        self.assertEqual(computation.upper_limit, 65023)
        self.assertEqual(computation.offset, 0.0)
        self.assertEqual(computation.numerator, 1)
        self.assertEqual(computation.denominator, 64)
        self.assertEqual(computation.unit, "km/h")
        computation = attr.computations[1]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 65024)
        self.assertEqual(computation.upper_limit, 65279)
        self.assertEqual(len(computation.values), 1)
        self.assertEqual(computation[0], "Error")
        computation = attr.computations[2]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 65280)
        self.assertEqual(computation.upper_limit, 65535)
        self.assertEqual(len(computation.values), 1)
        self.assertEqual(computation[0], "NotAvailable")
