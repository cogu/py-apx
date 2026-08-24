"""
Unit tests for node parser
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
import apx.model as apx_model  # noqa E402
import apx.exception as apx_exception  # noqa E402
from apx.parser import (  # noqa E402
    NodeParser,
    split_type_declaration,
    split_port_declaration,
)


class TestSplitFunctions(unittest.TestCase):

    def test_split_type_declaration_simple(self):
        input_string = 'T"VehicleSpeed_T"S'
        result = split_type_declaration(input_string)
        self.assertEqual(result, ('VehicleSpeed_T', 'S', None))

    def test_split_type_declaration_with_limits(self):
        input_string = 'T"InactiveActive_T"C(0,3)'
        result = split_type_declaration(input_string)
        self.assertEqual(result, ('InactiveActive_T', 'C(0,3)', None))

    def test_split_type_declaration_with_limits_and_value_table(self):
        input_string = (
            'T"InactiveActive_T"C(0,3):'
            'VT("InactiveActive_Inactive","InactiveActive_Active","InactiveActive_Error","InactiveActive_NotAvailable")'
        )
        result = split_type_declaration(input_string)
        expected_vt = (
            'VT("InactiveActive_Inactive","InactiveActive_Active",'
            '"InactiveActive_Error","InactiveActive_NotAvailable")'
        )
        self.assertEqual(
            result,
            ('InactiveActive_T', 'C(0,3)', expected_vt)
        )

    def test_split_require_port_simple(self):
        input_string = 'R"VehicleSpeed"S'
        result = split_port_declaration(input_string)
        self.assertEqual(result, ('R', 'VehicleSpeed', 'S', None))

    def test_split_require_port_with_init_value(self):
        input_string = 'R"VehicleSpeed"S:=65535'
        result = split_port_declaration(input_string)
        self.assertEqual(result, ('R', 'VehicleSpeed', 'S', '=65535'))

        input_string = 'R"VehicleSpeed"S : =65535'
        result = split_port_declaration(input_string)
        self.assertEqual(result, ('R', 'VehicleSpeed', 'S ', ' =65535'))

    def test_split_require_port_with_typeref_and_initvalue(self):
        input_string = 'R"VehicleSpeed"T["VehicleSpeed_T]:=65535'
        result = split_port_declaration(input_string)
        self.assertEqual(result, ('R', 'VehicleSpeed', 'T["VehicleSpeed_T]', '=65535'))

    def test_split_provide_port_simple(self):
        input_string = 'P"VehicleSpeed"S'
        result = split_port_declaration(input_string)
        self.assertEqual(result, ('P', 'VehicleSpeed', 'S', None))


class TestNodeParser(unittest.TestCase):

    def test_parse_empty_node(self):
        apx_text = "APX/1.3\n" + 'N"EmptyNode"\n'
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(node.name, "EmptyNode")

    def test_parse_type_declaration(self):
        apx_text = """APX/1.3
N"TestNode"
T"Percentage_T"C
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(node.name, "TestNode")
        self.assertEqual(len(node.data_types), 1)
        data_type = node.data_types[0]
        self.assertEqual(data_type.name, 'Percentage_T')
        self.assertFalse(data_type.has_attributes)
        data_element = data_type.dsg.element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(data_element.has_limits)

    def test_parse_type_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
T"OnOff_T"C(0,3)
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        data_type = node.data_types[0]
        self.assertEqual(data_type.name, 'OnOff_T')
        self.assertFalse(data_type.has_attributes)
        data_element = data_type.dsg.element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.has_limits)
        self.assertEqual(data_element.lower_limit, 0)
        self.assertEqual(data_element.upper_limit, 3)

    def test_parse_type_with_value_table(self):
        apx_text = """APX/1.3
N"TestNode"
T"OnOff_T"C(0,3):VT("OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        data_type = node.data_types[0]
        self.assertEqual(data_type.name, 'OnOff_T')
        self.assertEqual(data_type.line_number, 3)
        data_element = data_type.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.has_limits)
        self.assertTrue(data_type.has_attributes)
        attr = data_type.attributes
        self.assertEqual(len(attr.computations), 1)
        computation = attr.computations[0]
        self.assertIsInstance(computation, apx_model.ValueTable)
        self.assertEqual(computation.lower_limit, 0)
        self.assertEqual(computation.upper_limit, 3)
        self.assertEqual(computation[0], "OnOff_Off")
        self.assertEqual(computation[1], "OnOff_On")
        self.assertEqual(computation[2], "OnOff_Error")
        self.assertEqual(computation[3], "OnOff_NotAvailable")

    def test_parse_require_port_declaration_no_init(self):
        apx_text = """APX/1.3
N"TestNode"
R"FuelLevel"C
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'FuelLevel')
        self.assertEqual(port.line_number, 3)
        self.assertFalse(port.has_attributes)
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)

    def test_parse_require_port_declaration_u8_array_no_init(self):
        apx_text = """APX/1.3
N"TestNode"
R"DataPoints"C[8]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'DataPoints')
        self.assertEqual(port.line_number, 3)
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 8)

    def test_parse_require_port_declaration_init(self):
        apx_text = """APX/1.3
N"TestNode"
R"FuelLevel"C:=255
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'FuelLevel')
        self.assertTrue(port.has_attributes)
        attributes = port.attributes
        self.assertEqual(attributes.init_value, 255)

    def test_parse_require_port_declaration_u8_with_range(self):
        apx_text = """APX/1.3
N"TestNode"
R"Value"C(0,3):=3
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'Value')
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(data_element.has_limits)
        self.assertEqual(data_element.lower_limit, 0)
        self.assertEqual(data_element.upper_limit, 3)
        self.assertTrue(port.has_attributes)
        attributes = port.attributes
        self.assertEqual(attributes.init_value, 3)

    def test_parse_require_port_declaration_u8_ref_no_init(self):
        apx_text = """APX/1.3
N"TestNode"
T"Percentage_T"C
R"FuelLevel1"T[0]
R"FuelLevel2"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'FuelLevel1')
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        data_type = data_element.typeref
        self.assertEqual(data_type.name, "Percentage_T")
        self.assertEqual(data_type.data_element.type_code, apx_base.TypeCode.UINT8)

    def test_parse_require_port_declaration_u8_ref_with_init(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type_T"C(0,3):VT("Off","On","Error","NotAvailable")
R"UInt8Port"T[0]:=3
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'UInt8Port')
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        data_type = data_element.typeref
        self.assertEqual(data_type.name, "Type_T")

    def test_parse_record_notification_t(self):
        apx_text = """APX/1.3
N"TestNode"
T"Notification_T"{"ID"C(0,127)"Stat"C(0,3)"Type"C(0,7)}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        data_type = node.data_types[0]
        self.assertEqual(data_type.name, 'Notification_T')
        data_element = data_type.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.name, "ID")
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)
        child_element = data_element.elements[1]
        self.assertEqual(child_element.name, "Stat")
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)
        child_element = data_element.elements[2]
        self.assertEqual(child_element.name, "Type")
        self.assertEqual(child_element.type_code, apx_base.TypeCode.UINT8)

    def test_parse_error_in_record(self):
        apx_text = """APX/1.3
N"TestNode"
T"Notification_T"{{"ID"C(0,127)"Stat"C(0,3)"Type"C(0,7)}
"""
        parser = NodeParser()
        with self.assertRaises(apx_exception.ParseError):
            parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.PARSE_ERROR)

    def test_parse_queued_provide_port_with_uint8_queue_size(self):
        apx_text = """APX/1.3
N"TestNode"
P"U8Signal"C:Q[10]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        self.assertEqual(port.name, "U8Signal")
        attr = port.attributes
        self.assertTrue(attr.is_queued)
        self.assertEqual(attr.queue_length, 10)

    def test_parse_char(self):
        apx_text = """APX/1.3
N"TestNode"
P"CharSignal"a
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)

    def test_parse_char_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"CharSignal"a[10]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 10)

    def test_parse_char_array_with_empty_string_initializer(self):
        apx_text = """APX/1.3
N"TestNode"
P"CharSignal"a[10]:=""
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 10)

    def test_parse_char8(self):
        apx_text = """APX/1.3
N"TestNode"
P"CharSignal"A
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.CHAR8)
        self.assertFalse(data_element.is_array)


class TestNodeTypeReferences(unittest.TestCase):

    def test_parse_record_type_ref_containing_element_typerefs_by_id(self):
        apx_text = """APX/1.3
N"TestNode"
T"FirstType_T"C(0,3)
T"SecondType_T"C(0,7)
T"RecordType_T"{"First"T[0]"Second"T[1]}
R"RecordPort"T[2]:={3,7}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.name, 'RecordPort')
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        data_type = data_element.typeref
        self.assertEqual(data_type.name, "RecordType_T")
        child_element = data_type.data_element.elements[0]
        self.assertEqual(child_element.name, "First")
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        ref_child_type = child_element.typeref
        ref_child_element = ref_child_type.data_element
        self.assertEqual(ref_child_element.type_code, apx_base.TypeCode.UINT8)
        child_element = data_type.data_element.elements[1]
        self.assertEqual(child_element.name, "Second")
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        ref_child_type = child_element.typeref
        ref_child_element = ref_child_type.data_element
        self.assertEqual(ref_child_element.type_code, apx_base.TypeCode.UINT8)

    def test_record_of_records(self):
        apx_text = """APX/1.3
N"TestNode"
T"FirstType_T"{"Inner1"C"Inner2"S}
T"SecondType_T"{"Inner3"S\"Inner4"L}
T"RecordOfRecordType_T"{"First"T[0]"Second"T[1]}
R"RecordPort"T[2]:={ {3,0xFFFF}, {0xFFFF, 0xFFFFFFFF} }
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertFalse(data_element.is_array)
        data_type = data_element.typeref
        ref_data_element = data_type.data_element
        self.assertEqual(ref_data_element.type_code, apx_base.TypeCode.RECORD)

    def test_array_of_records_using_type_ref(self):
        apx_text = """APX/1.3
N"TestNode"
T"RecordType_T"{"Id"S"Value"C}
R"RecordPort"T[0][2]:={ {0xFFFF, 0}, {0xFFFF, 0} }
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        data_element = port.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertTrue(data_element.is_array)
        self.assertEqual(data_element.array_len, 2)
        data_type = data_element.typeref
        ref_data_element = data_type.data_element
        self.assertEqual(ref_data_element.type_code, apx_base.TypeCode.RECORD)

    def test_recursive_follow_typeref_by_id(self):
        apx_text = """APX/1.3
N"TestNode"
T"UserName_T"a[20]
T"UserId_T"L
T"UserInfo_T"{"UserName"T[0]"UserId"T[1]}
R"UserInfo"T[2]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.line_number, 6)
        port_data_element = port.data_element
        self.assertEqual(port_data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        data_element = port_data_element.typeref.data_element

        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)
        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertEqual(child_element.name, "UserName")
        datatype = child_element.typeref
        grand_child_element = datatype.data_element
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.CHAR)
        self.assertEqual(grand_child_element.array_len, 20)

        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertEqual(child_element.name, "UserId")
        datatype = child_element.typeref
        grand_child_element = datatype.data_element
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT32)
        self.assertFalse(grand_child_element.is_array)

    def test_follow_typeref_by_name(self):
        apx_text = """APX/1.3
N"TestNode"
T"Percentage_T"C
R"FuelLevel"T["Percentage_T"]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.line_number, 4)
        port_data_element = port.data_element
        self.assertEqual(port_data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        data_element = port_data_element.typeref.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.UINT8)

    def test_recursive_follow_typeref_by_name(self):
        apx_text = """APX/1.3
N"TestNode"
T"UserName_T"a[20]
T"UserId_T"L
T"UserInfo_T"{"UserName"T["UserName_T"]"UserId"T["UserId_T"]}
R"UserInfo"T["UserInfo_T"]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.line_number, 6)
        port_data_element = port.data_element
        self.assertEqual(port_data_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        port_data_type = port_data_element.typeref
        self.assertEqual(port_data_type.name, "UserInfo_T")
        data_element = port_data_type.data_element
        self.assertEqual(data_element.type_code, apx_base.TypeCode.RECORD)

        child_element = data_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertEqual(child_element.name, "UserName")
        datatype = child_element.typeref
        grand_child_element = datatype.data_element
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.CHAR)
        self.assertEqual(grand_child_element.array_len, 20)

        child_element = data_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.TYPE_REF_PTR)
        self.assertEqual(child_element.name, "UserId")
        datatype = child_element.typeref
        grand_child_element = datatype.data_element
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT32)
        self.assertFalse(grand_child_element.is_array)


class TestNodeInitValues(unittest.TestCase):

    def test_derive_proper_init_value_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"C:=0
R"Signal2"C:=255
R"Signal3"C:=0xFF
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3 = node.require_ports[0:3]
        self.assertEqual(port1.proper_init_value, 0)
        self.assertEqual(port2.proper_init_value, 255)
        self.assertEqual(port3.proper_init_value, 255)

    def test_derive_proper_init_value_uint16(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"S:=0
R"Signal2"S:=65535
R"Signal3"S:=0xFFFF
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3 = node.require_ports[0:3]
        self.assertEqual(port1.proper_init_value, 0)
        self.assertEqual(port2.proper_init_value, 65535)
        self.assertEqual(port3.proper_init_value, 65535)

    def test_derive_proper_init_value_uint32(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"L:=0
R"Signal2"L:=4294967295
R"Signal3"L:=0xFFFFFFFF
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3 = node.require_ports[0:3]
        self.assertEqual(port1.proper_init_value, 0)
        self.assertEqual(port2.proper_init_value, 4294967295)
        self.assertEqual(port3.proper_init_value, 4294967295)

    def test_derive_proper_init_value_uint64(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"Q:=0
R"Signal2"Q:=18446744073709551615
R"Signal3"Q:=0xFFFFFFFFFFFFFFFF
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3 = node.require_ports[0:3]
        self.assertEqual(port1.proper_init_value, 0)
        self.assertEqual(port2.proper_init_value, 18446744073709551615)
        self.assertEqual(port3.proper_init_value, 18446744073709551615)

    def test_derive_proper_init_value_int8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"c:=-128
R"Signal2"c:=-1
R"Signal3"c:=0
R"Signal4"c:=127
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3, port4 = node.require_ports[0:4]
        self.assertEqual(port1.proper_init_value, -128)
        self.assertEqual(port2.proper_init_value, -1)
        self.assertEqual(port3.proper_init_value, 0)
        self.assertEqual(port4.proper_init_value, 127)

    def test_derive_proper_init_value_int16(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"s:=-32768
R"Signal2"s:=-1
R"Signal3"s:=0
R"Signal4"s:=32767
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3, port4 = node.require_ports[0:4]
        self.assertEqual(port1.proper_init_value, -32768)
        self.assertEqual(port2.proper_init_value, -1)
        self.assertEqual(port3.proper_init_value, 0)
        self.assertEqual(port4.proper_init_value, 32767)

    def test_derive_proper_init_value_int32(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"l:=-2147483648
R"Signal2"l:=-1
R"Signal3"l:=0
R"Signal4"l:=2147483647
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3, port4 = node.require_ports[0:4]
        self.assertEqual(port1.proper_init_value, -2147483648)
        self.assertEqual(port2.proper_init_value, -1)
        self.assertEqual(port3.proper_init_value, 0)
        self.assertEqual(port4.proper_init_value, 2147483647)

    def test_derive_proper_init_value_int64(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal1"q:=-9223372036854775808
R"Signal2"q:=-1
R"Signal3"q:=0
R"Signal4"q:=9223372036854775807
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port1, port2, port3, port4 = node.require_ports[0:4]
        self.assertEqual(port1.proper_init_value, -9223372036854775808)
        self.assertEqual(port2.proper_init_value, -1)
        self.assertEqual(port3.proper_init_value, 0)
        self.assertEqual(port4.proper_init_value, 9223372036854775807)

    def test_derive_proper_init_value_uint8_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C[4]:={0,1,2,3}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, [0, 1, 2, 3])

    def test_derive_empty_initializer_uint8_dynamic_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C[4096*]:={}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, [])

    def test_derive_proper_init_value_uint8_record(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"{"Red"C"Green"C"Blue"C}:={0xFF, 0xFF, 0xFF}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, {"Red": 255, "Green": 255, "Blue": 255})

    def test_derive_proper_init_value_uint8_record_typeref_by_id(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"{"Red"C"Green"C"Blue"C}
R"Signal"T[0]:={0xFF, 0xFF, 0xFF}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, {"Red": 255, "Green": 255, "Blue": 255})

    def test_derive_proper_init_value_uint8_record_typeref_by_name(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"{"Red"C"Green"C"Blue"C}
R"Signal"T["Type"]:={0xFF, 0xFF, 0xFF}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, {"Red": 255, "Green": 255, "Blue": 255})

    def test_derive_proper_init_value_uint8_record_array_with_typeref(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"{"Red"C"Green"C"Blue"C}
R"Signal"T[0][2]:={{0xFF, 0xFF, 0xFF}, {0, 0, 0}}
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        expected_init = [{"Red": 255, "Green": 255, "Blue": 255}, {"Red": 0, "Green": 0, "Blue": 0}]
        self.assertEqual(port.proper_init_value, expected_init)

    def test_derive_proper_init_value_char_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"a[10]:="hello"
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, "hello")

    def test_derive_proper_init_value_char_array_invalid_ascii(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"a[10]:="café"
"""
        parser = NodeParser()
        with self.assertRaises(apx_exception.ParseError):
            parser.loads(apx_text)

    def test_derive_proper_init_value_char8_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"A[10]:="café"
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.require_ports[0]
        self.assertEqual(port.proper_init_value, "café")


class TestNodeEffectiveElements(unittest.TestCase):

    def test_effective_element_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(effective_element.has_limits)
        self.assertFalse(effective_element.is_array)

    def test_effective_element_uint8_ref_by_id(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C
P"Signal"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertFalse(effective_element.has_limits)
        self.assertFalse(effective_element.is_array)

    def test_effective_element_uint8_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C(0,7)
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertFalse(effective_element.is_array)

    def test_effective_element_uint8_ref_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C(0,7)
P"Signal"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertFalse(effective_element.is_array)

    def test_effective_element_ref_to_uint8_array(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C(0,7)[10]
P"Signal"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertTrue(effective_element.is_array)
        self.assertEqual(effective_element.array_len, 10)

    def test_effective_element_array_ref_to_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C(0,7)
P"Signal"T[0][12]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertTrue(effective_element.is_array)
        self.assertEqual(effective_element.array_len, 12)

    def test_effective_element_ref_to_uint8_dyn_array(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C(0,7)[100*]
P"Signal"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertTrue(effective_element.is_array)
        self.assertTrue(effective_element.is_dynamic_array)
        self.assertEqual(effective_element.array_len, 100)

    def test_effective_element_dyn_array_ref_to_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"C(0,7)
P"Signal"T[0][120*]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(effective_element.has_limits)
        self.assertEqual(effective_element.lower_limit, 0)
        self.assertEqual(effective_element.upper_limit, 7)
        self.assertTrue(effective_element.is_array)
        self.assertTrue(effective_element.is_dynamic_array)
        self.assertEqual(effective_element.array_len, 120)

    def test_effective_element_ref_to_dynamic_uint8_record_array(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"{"Red"C"Green"C"Blue"C}[50*]
P"Signal"T[0]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(effective_element.has_limits)
        self.assertTrue(effective_element.is_array)
        self.assertTrue(effective_element.is_dynamic_array)
        self.assertEqual(effective_element.array_len, 50)

    def test_effective_element_dyn_array_ref_to_uint8_record(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type"{"Red"C"Green"C"Blue"C}
P"Signal"T[0][50*]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(effective_element.has_limits)
        self.assertTrue(effective_element.is_array)
        self.assertTrue(effective_element.is_dynamic_array)
        self.assertEqual(effective_element.array_len, 50)

    def test_effective_element_array_ref_to_record_with_record_ref(self):
        apx_text = """APX/1.3
N"TestNode"
T"Point_T"{"X"C"Y"C}
T"Color_T"{"Red"C"Green"C"Blue"C}
T"Type_T"{"Point"T["Point_T"]"Color"T["Color_T"]}
P"Signal"T["Type_T"][4]
"""
        parser = NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        port = node.provide_ports[0]
        effective_element = port.effective_element
        self.assertEqual(effective_element.type_code, apx_base.TypeCode.RECORD)
        self.assertFalse(effective_element.has_limits)
        self.assertTrue(effective_element.is_array)
        self.assertFalse(effective_element.is_dynamic_array)
        self.assertEqual(effective_element.array_len, 4)
        self.assertEqual(len(effective_element.elements), 2)
        self.assertEqual(effective_element.elements[0].name, "Point")
        self.assertEqual(effective_element.elements[1].name, "Color")
        child_element = effective_element.elements[0]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(child_element.elements), 2)
        grand_child_element = child_element.elements[0]
        self.assertEqual(grand_child_element.name, "X")
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT8)
        grand_child_element = child_element.elements[1]
        self.assertEqual(grand_child_element.name, "Y")
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT8)
        child_element = effective_element.elements[1]
        self.assertEqual(child_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(child_element.elements), 3)
        grand_child_element = child_element.elements[0]
        self.assertEqual(grand_child_element.name, "Red")
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT8)
        grand_child_element = child_element.elements[1]
        self.assertEqual(grand_child_element.name, "Green")
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT8)
        grand_child_element = child_element.elements[2]
        self.assertEqual(grand_child_element.name, "Blue")
        self.assertEqual(grand_child_element.type_code, apx_base.TypeCode.UINT8)


if __name__ == '__main__':
    unittest.main()
