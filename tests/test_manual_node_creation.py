"""
Unit tests for manual node creation and translation to apx.model.Node using NodeParser
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
import apx.model as apx_model  # noqa E402
import apx.exception as apx_exception  # noqa E402
from apx.parser import NodeParser  # noqa E402
from apx.vm.compiler import Compiler  # noqa E402
from apx.vm.base import ProgramType  # noqa E402
from apx.vm import VirtualMachine  # noqa E402


class TestNodeCreation(unittest.TestCase):

    def test_create_empty_node(self):
        base_node = apx_base.Node('TestNode')
        self.assertIsInstance(base_node, apx_base.Node)
        self.assertEqual(base_node.name, 'TestNode')
        self.assertEqual(len(base_node.require_ports), 0)
        self.assertEqual(len(base_node.provide_ports), 0)

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertIsInstance(model_node, apx_model.Node)
        self.assertEqual(model_node.name, 'TestNode')
        self.assertTrue(model_node.is_finalized)
        self.assertEqual(len(model_node.require_ports), 0)
        self.assertEqual(len(model_node.provide_ports), 0)

    def test_create_require_port_uint8(self):
        base_node = apx_base.Node('TestNode')
        port = base_node.append(apx_base.RequirePort('U8Signal', 'C', '=255'))
        self.assertIsInstance(port, apx_base.RequirePort)
        self.assertEqual(len(base_node.require_ports), 1)

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(len(model_node.require_ports), 1)
        model_port = model_node.require_ports[0]
        self.assertIsInstance(model_port, apx_model.RequirePort)
        self.assertEqual(model_port.name, 'U8Signal')
        self.assertEqual(model_port.effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(model_port.proper_init_value, 255)

    def test_create_provide_port_with_limits_and_init_value(self):
        base_node = apx_base.Node('DemoSender')
        base_node.append(apx_base.ProvidePort('DemoSignal', 'C(0,15)', '=15'))

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(len(model_node.provide_ports), 1)
        model_port = model_node.provide_ports[0]
        self.assertIsInstance(model_port, apx_model.ProvidePort)
        self.assertEqual(model_port.name, 'DemoSignal')
        self.assertEqual(model_port.effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(model_port.effective_element.lower_limit, 0)
        self.assertEqual(model_port.effective_element.upper_limit, 15)
        self.assertEqual(model_port.proper_init_value, 15)

    def test_create_node_with_data_type_and_reference(self):
        base_node = apx_base.Node('TestNode')
        base_node.append(apx_base.DataType('VehicleSpeed_T', 'S'))
        base_node.append(apx_base.RequirePort('VehicleSpeed', 'T["VehicleSpeed_T"]', '=65535'))

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        self.assertEqual(len(model_node.data_types), 1)
        self.assertEqual(len(model_node.require_ports), 1)

        model_type = model_node.data_types[0]
        self.assertEqual(model_type.name, 'VehicleSpeed_T')
        self.assertEqual(model_type.data_element.type_code, apx_base.TypeCode.UINT16)

        model_port = model_node.require_ports[0]
        self.assertEqual(model_port.name, 'VehicleSpeed')
        self.assertEqual(model_port.effective_element.type_code, apx_base.TypeCode.UINT16)
        self.assertEqual(model_port.proper_init_value, 65535)

    def test_create_node_with_value_table(self):
        base_node = apx_base.Node('TestNode')
        base_node.append(
            apx_base.DataType(
                'InactiveActive_T',
                'C(0,3)',
                'VT("InactiveActive_Inactive","InactiveActive_Active",'
                '"InactiveActive_Error","InactiveActive_NotAvailable")'
            )
        )
        base_node.append(apx_base.ProvidePort('Status', 'T["InactiveActive_T"]', '=0'))

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        model_port = model_node.provide_ports[0]
        self.assertEqual(model_port.name, 'Status')
        self.assertEqual(model_port.proper_init_value, 0)

    def test_create_record_and_array_ports(self):
        base_node = apx_base.Node('SensorNode')
        base_node.append(apx_base.ProvidePort('Coords', '{"X"S"Y"S}', '={100, 200}'))
        base_node.append(apx_base.RequirePort('Values', 'C[4]', '={1, 2, 3, 4}'))

        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        coords_port = model_node.provide_ports[0]
        self.assertEqual(coords_port.effective_element.type_code, apx_base.TypeCode.RECORD)
        self.assertEqual(len(coords_port.effective_element.elements), 2)
        self.assertEqual(coords_port.proper_init_value, {'X': 100, 'Y': 200})

        values_port = model_node.require_ports[0]
        self.assertEqual(values_port.effective_element.type_code, apx_base.TypeCode.UINT8)
        self.assertTrue(values_port.effective_element.is_array)
        self.assertEqual(values_port.effective_element.array_len, 4)
        self.assertEqual(values_port.proper_init_value, [1, 2, 3, 4])

    def test_compiler_and_vm_execution_from_programmatic_node(self):
        # Create a programmatic node
        base_node = apx_base.Node('DemoSender')
        base_node.append(apx_base.ProvidePort('DemoSignal', 'C(0,15)', '=15'))

        # Translate to model
        parser = NodeParser()
        model_node = parser.from_base_node(base_node)
        self.assertEqual(parser.result, apx_base.Result.NO_ERROR)
        provide_port = model_node.provide_ports[0]

        # Compile pack program
        compiler = Compiler()
        result, pack_bytecode = compiler.compile_port(provide_port, ProgramType.PACK)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertIsNotNone(pack_bytecode)

        # Execute pack on VM
        vm = VirtualMachine()
        result = vm.select_program(pack_bytecode)
        self.assertEqual(result, apx_base.Result.NO_ERROR)

        out_buffer = bytearray(1)
        vm.set_write_buffer(out_buffer)
        result = vm.pack_value(7)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual(out_buffer, bytearray([7]))

    def test_invalid_signature_raises_parse_error(self):
        base_node = apx_base.Node('ErrorNode')
        base_node.append(apx_base.ProvidePort('BadPort', 'C('))  # Invalid syntax

        parser = NodeParser()
        with self.assertRaises(apx_exception.ParseError):
            parser.from_base_node(base_node)

    def test_invalid_attribute_raises_parse_error(self):
        base_node = apx_base.Node('ErrorNode')
        base_node.append(apx_base.ProvidePort('BadPort', 'C', '=@bad'))

        parser = NodeParser()
        with self.assertRaises(apx_exception.ParseError):
            parser.from_base_node(base_node)

    def test_missing_type_reference_raises_parse_error(self):
        base_node = apx_base.Node('ErrorNode')
        base_node.append(apx_base.RequirePort('Port1', 'T["MissingType"]'))

        parser = NodeParser()
        with self.assertRaises(apx_exception.ParseError):
            parser.from_base_node(base_node)

    def test_non_base_node_raises_type_error(self):
        parser = NodeParser()
        with self.assertRaises(TypeError):
            parser.from_base_node("not a node")


    def _create_unsorted_model_node(self) -> apx_model.Node:
        node = apx_model.Node('TestNode')
        for name in ['Zebra_T', 'Alpha_T', 'Beta_T']:
            dt = apx_model.DataType(name)
            dt.data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
            node.append(dt)
        for name in ['ZuluPort', 'AlphaPort']:
            rp = apx_model.RequirePort(name)
            rp.data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
            node.append(rp)
        for name in ['YankeePort', 'BravoPort']:
            pp = apx_model.ProvidePort(name)
            pp.data_element = apx_model.DataElement(apx_base.TypeCode.UINT8)
            node.append(pp)
        return node

    def test_finalize_default_sorts_lists_alphabetically(self):
        node = self._create_unsorted_model_node()
        result = node.finalize()
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual([t.name for t in node.data_types], ['Alpha_T', 'Beta_T', 'Zebra_T'])
        self.assertEqual([p.name for p in node.require_ports], ['AlphaPort', 'ZuluPort'])
        self.assertEqual([p.name for p in node.provide_ports], ['BravoPort', 'YankeePort'])

    def test_finalize_sort_false_preserves_order(self):
        node = self._create_unsorted_model_node()
        result = node.finalize(sort=False)
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual([t.name for t in node.data_types], ['Zebra_T', 'Alpha_T', 'Beta_T'])
        self.assertEqual([p.name for p in node.require_ports], ['ZuluPort', 'AlphaPort'])
        self.assertEqual([p.name for p in node.provide_ports], ['YankeePort', 'BravoPort'])


if __name__ == '__main__':
    unittest.main()
