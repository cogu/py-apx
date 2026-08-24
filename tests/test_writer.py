"""
Unit tests for APX writer
"""
# pylint: disable=missing-class-docstring, missing-function-docstring, implicit-str-concat
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx  # noqa E402
import apx.base as apx_base  # noqa E402
import apx.model as apx_model  # noqa E402
from apx.parser import NodeParser  # noqa E402
from apx.writer import Writer  # noqa E402


class TestWriterBasicPorts(unittest.TestCase):

    def test_write_single_provide_port_uint8(self):
        node = apx.Node('TestNode')
        node.append(apx.ProvidePort('U8Signal', 'C'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'P"U8Signal"C')

        full_str = writer.write_str(node)
        expected = "APX/1.3\n" 'N"TestNode"\n' 'P"U8Signal"C'
        self.assertEqual(full_str, expected)

    def test_write_single_provide_port_uint8_with_init_value(self):
        node = apx.Node('TestNode')
        node.append(apx.ProvidePort('U8Signal', 'C', '=255'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'P"U8Signal"C:=255')

    def test_write_single_require_port_uint16(self):
        node = apx.Node('TestNode')
        node.append(apx.RequirePort('U16Signal', 'S'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'R"U16Signal"S')

    def test_write_single_require_port_uint16_with_init_value(self):
        node = apx.Node('TestNode')
        node.append(apx.RequirePort('U16Signal', 'S', '=65535'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'R"U16Signal"S:=65535')

    def test_write_single_require_port_uint32(self):
        node = apx.Node('TestNode')
        node.append(apx.RequirePort('U32Signal', 'L'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'R"U32Signal"L')

    def test_write_single_require_port_uint32_with_init_value(self):
        node = apx.Node('TestNode')
        node.append(apx.RequirePort('U32Signal', 'L', '=4294967295'))

        writer = Writer()
        body = writer.write_body_str(node)
        self.assertEqual(body, 'R"U32Signal"L:=4294967295')


class TestWriterHeaderAndBody(unittest.TestCase):

    def test_write_header_str_default_v13(self):
        node = apx.Node('SensorNode')
        writer = Writer()
        header = writer.write_header_str(node)
        expected = "APX/1.3\n" 'N"SensorNode"'
        self.assertEqual(header, expected)

    def test_write_header_str_v12(self):
        node = apx.Node('SensorNode')
        writer = Writer()
        header = writer.write_header_str(node, version="APX/1.2")
        expected = "APX/1.2\n" 'N"SensorNode"'
        self.assertEqual(header, expected)

    def test_write_empty_node(self):
        node = apx.Node('EmptyNode')
        writer = Writer()
        full_str = writer.write_str(node)
        expected = "APX/1.3\n" 'N"EmptyNode"'
        self.assertEqual(full_str, expected)

        body = writer.write_body_str(node)
        self.assertEqual(body, '')


class TestWriterMultiplePortsAndTypes(unittest.TestCase):

    def test_write_multiple_ports(self):
        node = apx.Node('MultiPortNode')
        node.append(apx.ProvidePort('Out1', 'C', '=0'))
        node.append(apx.ProvidePort('Out2', 'S', '=1000'))
        node.append(apx.RequirePort('In1', 'L', '=0'))
        node.append(apx.RequirePort('In2', 'a[10]', '=""'))

        writer = Writer()
        body = writer.write_body_str(node)
        expected = (
            'P"Out1"C:=0\n'
            'P"Out2"S:=1000\n'
            'R"In1"L:=0\n'
            'R"In2"a[10]:=""'
        )
        self.assertEqual(body, expected)

    def test_write_data_type_and_type_reference_v13(self):
        node = apx.Node('TypeRefNode')
        node.append(apx.DataType('VehicleSpeed_T', 'S'))
        node.append(apx.RequirePort('VehicleSpeed', 'T["VehicleSpeed_T"]', '=65535'))

        writer = Writer()
        body = writer.write_body_str(node, version="APX/1.3")
        expected = (
            'T"VehicleSpeed_T"S\n'
            'R"VehicleSpeed"T["VehicleSpeed_T"]:=65535'
        )
        self.assertEqual(body, expected)

    def test_write_data_type_and_type_reference_v12(self):
        node = apx.Node('TypeRefNode')
        node.append(apx.DataType('VehicleSpeed_T', 'S'))
        node.append(apx.RequirePort('VehicleSpeed', 'T["VehicleSpeed_T"]', '=65535'))

        writer = Writer()
        body = writer.write_body_str(node, version="APX/1.2")
        expected = (
            'T"VehicleSpeed_T"S\n'
            'R"VehicleSpeed"T[0]:=65535'
        )
        self.assertEqual(body, expected)

    def test_write_multiple_data_types_v12(self):
        node = apx.Node('MultiTypeNode')
        node.append(apx.DataType('TypeA', 'C'))
        node.append(apx.DataType('TypeB', 'S'))
        node.append(apx.DataType('TypeC', 'L'))
        node.append(apx.ProvidePort('PortA', 'T["TypeA"]'))
        node.append(apx.ProvidePort('PortB', 'T["TypeB"]'))
        node.append(apx.RequirePort('PortC', 'T["TypeC"]'))

        writer = Writer()
        body = writer.write_body_str(node, version="APX/1.2")
        expected = (
            'T"TypeA"C\n'
            'T"TypeB"S\n'
            'T"TypeC"L\n'
            'P"PortA"T[0]\n'
            'P"PortB"T[1]\n'
            'R"PortC"T[2]'
        )
        self.assertEqual(body, expected)


class TestWriterComplexTypes(unittest.TestCase):

    def test_write_limits_and_arrays(self):
        node = apx.Node('LimitsNode')
        node.append(apx.ProvidePort('LimitedSignal', 'C(0,15)', '=15'))
        node.append(apx.RequirePort('ArraySignal', 'S[4]', '={1, 2, 3, 4}'))
        node.append(apx.RequirePort('DynArraySignal', 'C[4096*]', '={}'))

        writer = Writer()
        body = writer.write_body_str(node)
        expected = (
            'P"LimitedSignal"C(0,15):=15\n'
            'R"ArraySignal"S[4]:={1, 2, 3, 4}\n'
            'R"DynArraySignal"C[4096*]:={}'
        )
        self.assertEqual(body, expected)

    def test_write_record_type(self):
        node = apx.Node('RecordNode')
        node.append(apx.DataType('Rgb_T', '{"Red"C"Green"C"Blue"C}'))
        node.append(apx.ProvidePort('Color', 'T["Rgb_T"]', '={255, 128, 0}'))

        writer = Writer()
        body_v13 = writer.write_body_str(node, version="APX/1.3")
        expected_v13 = (
            'T"Rgb_T"{"Red"C"Green"C"Blue"C}\n'
            'P"Color"T["Rgb_T"]:={255, 128, 0}'
        )
        self.assertEqual(body_v13, expected_v13)

        body_v12 = writer.write_body_str(node, version="APX/1.2")
        expected_v12 = (
            'T"Rgb_T"{"Red"C"Green"C"Blue"C}\n'
            'P"Color"T[0]:={255, 128, 0}'
        )
        self.assertEqual(body_v12, expected_v12)


class TestWriterAttributes(unittest.TestCase):

    def test_write_port_attributes_parameter_and_queue(self):
        node = apx.Node('AttrNode')
        node.append(apx.ProvidePort('ParamPort', 'C', '=10, P'))
        node.append(apx.RequirePort('QueuedPort', 'S', 'Q[5]'))

        writer = Writer()
        body = writer.write_body_str(node)
        expected = (
            'P"ParamPort"C:=10, P\n'
            'R"QueuedPort"S:Q[5]'
        )
        self.assertEqual(body, expected)

    def test_write_type_attributes_value_table(self):
        node = apx.Node('VtNode')
        node.append(
            apx.DataType(
                'OnOff_T',
                'C(0,3)',
                'VT("OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")'
            )
        )
        node.append(apx.ProvidePort('State', 'T["OnOff_T"]', '=0'))

        writer = Writer()
        body = writer.write_body_str(node)
        expected = (
            'T"OnOff_T"C(0,3):VT("OnOff_Off", "OnOff_On", "OnOff_Error", "OnOff_NotAvailable")\n'
            'P"State"T["OnOff_T"]:=0'
        )
        self.assertEqual(body, expected)

    def test_write_type_attributes_rational_scaling(self):
        node = apx.Node('RsNode')
        node.append(
            apx.DataType(
                'Speed_T',
                'S(0,65280)',
                'RS(0, 65280, 0, 1, 64, "km/h")'
            )
        )
        node.append(apx.RequirePort('Speed', 'T["Speed_T"]', '=0'))

        writer = Writer()
        body = writer.write_body_str(node)
        expected = (
            'T"Speed_T"S(0,65280):RS(0, 65280, 0, 1, 64, "km/h")\n'
            'R"Speed"T["Speed_T"]:=0'
        )
        self.assertEqual(body, expected)


class TestWriterModelNodeDirect(unittest.TestCase):

    def test_write_model_node_directly(self):
        model_node = apx_model.Node('DirectModelNode')
        u8_elem = apx_model.DataElement(apx_base.TypeCode.UINT8)
        model_port = apx_model.ProvidePort('U8Direct')
        model_port.data_element = u8_elem
        model_node.append(model_port)

        writer = Writer()
        body = writer.write_body_str(model_node)
        self.assertEqual(body, 'P"U8Direct"C')

        full_str = writer.write_str(model_node)
        expected = "APX/1.3\n" 'N"DirectModelNode"\n' 'P"U8Direct"C'
        self.assertEqual(full_str, expected)


class TestWriterFile(unittest.TestCase):

    def test_write_file(self):
        node = apx.Node('FileTestNode')
        node.append(apx.ProvidePort('Port1', 'C', '=0'))
        node.append(apx.RequirePort('Port2', 'S', '=65535'))

        writer = Writer()
        expected_str = writer.write_str(node)

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.apx') as tf:
            temp_path = tf.name

        try:
            writer.write_file(node, temp_path)
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, expected_str)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestWriterVersionAndErrors(unittest.TestCase):

    def test_invalid_version_string(self):
        node = apx.Node('TestNode')
        writer = Writer()
        with self.assertRaises(ValueError):
            writer.write_str(node, version="invalid")

    def test_unsupported_version_number(self):
        node = apx.Node('TestNode')
        writer = Writer()
        with self.assertRaises(ValueError):
            writer.write_str(node, version="APX/2.0")

    def test_invalid_node_type(self):
        writer = Writer()
        with self.assertRaises(TypeError):
            writer.write_str("NotANode")


class TestWriterRoundtrip(unittest.TestCase):

    def test_roundtrip_with_parser(self):
        base_node = apx.Node('RoundtripNode')
        base_node.append(
            apx.DataType(
                'VehicleSpeed_T',
                'S(0,65280)',
                'RS(0, 65280, 0, 1, 64, "km/h")'
            )
        )
        base_node.append(apx.ProvidePort('VehicleSpeed', 'T["VehicleSpeed_T"]', '=0'))
        base_node.append(apx.RequirePort('EngineSpeed', 'S', '=0xFFFF'))

        writer = Writer()
        apx_text = writer.write_str(base_node)

        parser = NodeParser()
        parsed_node = parser.loads(apx_text)

        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(parsed_node.name, 'RoundtripNode')
        self.assertEqual(len(parsed_node.data_types), 1)
        self.assertEqual(len(parsed_node.provide_ports), 1)
        self.assertEqual(len(parsed_node.require_ports), 1)
        self.assertEqual(parsed_node.provide_ports[0].name, 'VehicleSpeed')
        self.assertEqual(parsed_node.require_ports[0].name, 'EngineSpeed')


if __name__ == '__main__':
    unittest.main()
