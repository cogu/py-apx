"""
Unit tests for APX Virtual Machine unpacking
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx
import apx.base as apx_base
import apx.vm.base
import apx.vm.compiler
import apx.vm.machine


def compile_port(apx_text: str, is_pack: bool = False) -> bytes:
    parser = apx.parser.NodeParser()
    node = parser.loads(apx_text)
    assert parser.result == apx_base.NO_ERROR
    ports = node.require_ports if len(node.require_ports) > 0 else node.provide_ports
    port = ports[0]
    compiler = apx.vm.compiler.Compiler()
    prog_type = apx.vm.base.ProgramType.PACK if is_pack else apx.vm.base.ProgramType.UNPACK
    result, program = compiler.compile_port(port, prog_type)
    assert result == apx_base.NO_ERROR
    return bytes(program)


class TestVMUnpackScalar(unittest.TestCase):

    def test_unpack_uint8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x12])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 1)
        self.assertEqual(vm.value(), 0x12)

    def test_unpack_uint16(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"S\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x34, 0x12])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 2)
        self.assertEqual(vm.value(), 0x1234)

    def test_unpack_uint32(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"L\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x78, 0x56, 0x34, 0x12])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 4)
        self.assertEqual(vm.value(), 0x12345678)

    def test_unpack_uint64(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"Q\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(
            vm.set_read_buffer(bytes([0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11])),
            apx_base.NO_ERROR
        )
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 8)
        self.assertEqual(vm.value(), 0x1122334455667788)

    def test_unpack_int8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"c\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0xFB])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 1)
        self.assertEqual(vm.value(), -5)

    def test_unpack_int16(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"s\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x18, 0xFC])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 2)
        self.assertEqual(vm.value(), -1000)

    def test_unpack_int32(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"l\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x60, 0x79, 0xFE, 0xFF])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 4)
        self.assertEqual(vm.value(), -100000)

    def test_unpack_int64(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"q\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(
            vm.set_read_buffer(bytes([0x00, 0x0E, 0xFA, 0xD5, 0xFE, 0xFF, 0xFF, 0xFF])),
            apx_base.NO_ERROR
        )
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 8)
        self.assertEqual(vm.value(), -5000000000)

    def test_unpack_bool(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"b\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        self.assertEqual(vm.set_read_buffer(bytes([1])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), True)

        self.assertEqual(vm.set_read_buffer(bytes([0])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), False)

    def test_unpack_byte(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0xAB])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), 0xAB)

    def test_unpack_char(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"a\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(b'A'), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), 'A')

    def test_unpack_from_memoryview(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"S\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        large_buffer = bytes([0, 0, 0, 0, 0x34, 0x12, 0, 0])
        mv = memoryview(large_buffer)[4:6]
        self.assertEqual(vm.set_read_buffer(mv), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), 0x1234)


class TestVMUnpackRangeCheck(unittest.TestCase):

    def test_unpack_uint8_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C(0, 100)\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        # In range
        self.assertEqual(vm.set_read_buffer(bytes([50])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), 50)

        # Out of range
        self.assertEqual(vm.set_read_buffer(bytes([150])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.VALUE_RANGE_ERROR)

    def test_unpack_int32_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"l(-1000, 1000)\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        # In range (-500)
        self.assertEqual(vm.set_read_buffer(bytes([0x0C, 0xFE, 0xFF, 0xFF])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), -500)

        # Out of range (2000)
        self.assertEqual(vm.set_read_buffer(bytes([0xD0, 0x07, 0x00, 0x00])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.VALUE_RANGE_ERROR)


class TestVMUnpackArray(unittest.TestCase):

    def test_unpack_uint8_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C[3]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([10, 20, 30])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 3)
        self.assertEqual(vm.value(), [10, 20, 30])

    def test_unpack_uint16_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"S[2]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x00, 0x01, 0x00, 0x02])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 4)
        self.assertEqual(vm.value(), [0x0100, 0x0200])

    def test_unpack_char_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"a[6]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(b"Hello\x00"), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 6)
        self.assertEqual(vm.value(), "Hello")


class TestVMUnpackDynamicArray(unittest.TestCase):

    def test_unpack_dynamic_uint8_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C[8*]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        raw_data = bytes([3, 1, 2, 3, 0, 0, 0, 0, 0])
        self.assertEqual(vm.set_read_buffer(raw_data), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 4)
        self.assertEqual(vm.value(), [1, 2, 3])

    def test_unpack_dynamic_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"a[8*]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        raw_data = bytes([2, ord('H'), ord('i'), 0, 0, 0, 0, 0, 0])
        self.assertEqual(vm.set_read_buffer(raw_data), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 3)
        self.assertEqual(vm.value(), "Hi")


class TestVMUnpackRecord(unittest.TestCase):

    def test_unpack_record_u16_u8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"{"U16"S"U8"C}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x34, 0x12, 0x56])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 3)
        self.assertEqual(vm.value(), {"U16": 0x1234, "U8": 0x56})

    def test_unpack_record_with_dynamic_string_and_status(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"{"Name"a[8*]"Status"L}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        raw_data = bytes([2, ord('H'), ord('i'), 0, 0, 0, 0, 0, 0, 0x78, 0x56, 0x34, 0x12])
        self.assertEqual(vm.set_read_buffer(raw_data), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 13)
        self.assertEqual(vm.value(), {"Name": "Hi", "Status": 0x12345678})

    def test_unpack_record_with_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"{"Val"C(10, 50)}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        self.assertEqual(vm.set_read_buffer(bytes([30])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.value(), {"Val": 30})

        self.assertEqual(vm.set_read_buffer(bytes([100])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.VALUE_RANGE_ERROR)


class TestVMUnpackRecordArray(unittest.TestCase):

    def test_unpack_array_of_records(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"{"U16"S"U8"C}[2]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        self.assertEqual(vm.set_read_buffer(bytes([0x02, 0x01, 0x03, 0x05, 0x04, 0x06])), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 6)
        self.assertEqual(
            vm.value(),
            [
                {"U16": 0x0102, "U8": 0x03},
                {"U16": 0x0405, "U8": 0x06},
            ]
        )

    def test_unpack_array_of_records_with_dynamic_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"{"Label"a[4*]"Id"C}[2]\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        raw_data = bytes([
            3, ord('C'), ord('a'), ord('t'), 0, 10,
            1, ord('A'), 0, 0, 0, 20
        ])
        self.assertEqual(vm.set_read_buffer(raw_data), apx_base.NO_ERROR)
        self.assertEqual(vm.unpack_value(), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_read(), 12)
        self.assertEqual(
            vm.value(),
            [
                {"Label": "Cat", "Id": 10},
                {"Label": "A", "Id": 20},
            ]
        )


class TestVMUnpackErrorHandling(unittest.TestCase):

    def test_unpack_with_pack_program_fails(self):
        pack_program = compile_port('APX/1.3\n'
                                    'N"TestNode"\n'
                                    'P"Signal"C:=0\n', is_pack=True)
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(pack_program), apx_base.NO_ERROR)
        vm.set_read_buffer(bytes([10]))
        self.assertEqual(vm.unpack_value(), apx_base.INVALID_PROGRAM_ERROR)

    def test_unpack_without_program_fails(self):
        vm = apx.vm.VirtualMachine()
        vm.set_read_buffer(bytes([10]))
        self.assertEqual(vm.unpack_value(), apx_base.INVALID_PROGRAM_ERROR)


if __name__ == '__main__':
    unittest.main()
