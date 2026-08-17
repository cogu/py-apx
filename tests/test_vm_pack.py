"""
Unit tests for APX Virtual Machine packing
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


def compile_port(apx_text: str, is_pack: bool = True) -> bytes:
    parser = apx.parser.NodeParser()
    node = parser.loads(apx_text)
    assert parser.result == apx_base.NO_ERROR
    ports = node.provide_ports if len(node.provide_ports) > 0 else node.require_ports
    port = ports[0]
    compiler = apx.vm.compiler.Compiler()
    prog_type = apx.vm.base.ProgramType.PACK if is_pack else apx.vm.base.ProgramType.UNPACK
    result, program = compiler.compile_port(port, prog_type)
    assert result == apx_base.NO_ERROR
    return bytes(program)


class TestVMPackScalar(unittest.TestCase):

    def test_pack_uint8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"C:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0x12), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 1)
        self.assertEqual(buf, bytearray([0x12]))

    def test_pack_uint16(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"S:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(2)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0x1234), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 2)
        self.assertEqual(buf, bytearray([0x34, 0x12]))

    def test_pack_uint32(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"L:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(4)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0x12345678), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 4)
        self.assertEqual(buf, bytearray([0x78, 0x56, 0x34, 0x12]))

    def test_pack_uint64(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"Q:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(8)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0x1122334455667788), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 8)
        self.assertEqual(buf, bytearray([0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11]))

    def test_pack_int8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"c:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(-5), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 1)
        self.assertEqual(buf, bytearray([0xFB]))

    def test_pack_int16(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"s:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(2)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(-1000), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 2)
        self.assertEqual(buf, bytearray([0x18, 0xFC]))

    def test_pack_int32(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"l:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(4)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(-100000), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 4)
        self.assertEqual(buf, bytearray([0x60, 0x79, 0xFE, 0xFF]))

    def test_pack_int64(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"q:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(8)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(-5000000000), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 8)
        self.assertEqual(buf, bytearray([0x00, 0x0E, 0xFA, 0xD5, 0xFE, 0xFF, 0xFF, 0xFF]))

    def test_pack_bool(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"b:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(True), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([1]))

        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(False), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([0]))

    def test_pack_byte(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"C:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0xAB), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([0xAB]))

    def test_pack_char(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"a:=""\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value('A'), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray(b'A'))

    def test_pack_into_memoryview(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"S:=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        large_buffer = bytearray(16)
        mv = memoryview(large_buffer)[4:6]
        self.assertEqual(vm.set_write_buffer(mv), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(0x1234), apx_base.NO_ERROR)
        self.assertEqual(large_buffer[4:6], bytearray([0x34, 0x12]))


class TestVMPackRangeCheck(unittest.TestCase):

    def test_pack_uint8_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"C(0, 100):=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        # In range
        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(50), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([50]))

        # Out of range
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(150), apx_base.VALUE_RANGE_ERROR)

    def test_pack_int32_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"l(-1000, 1000):=0\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        # In range
        buf = bytearray(4)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(-500), apx_base.NO_ERROR)

        # Out of range
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value(2000), apx_base.VALUE_RANGE_ERROR)


class TestVMPackArray(unittest.TestCase):

    def test_pack_uint8_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"C[3]:={0, 0, 0}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(3)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value([10, 20, 30]), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([10, 20, 30]))

    def test_pack_uint16_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"S[2]:={0, 0}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(4)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value([0x0100, 0x0200]), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([0x00, 0x01, 0x00, 0x02]))

    def test_pack_char_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"a[6]:=""\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(6)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value("Hello"), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray(b"Hello\x00"))


class TestVMPackDynamicArray(unittest.TestCase):

    def test_pack_dynamic_uint8_array(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'R"Signal"C[8*]\n', is_pack=True)
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1 + 8)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value([1, 2, 3]), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 1 + 3)
        self.assertEqual(buf[0], 3)
        self.assertEqual(buf[1:4], bytearray([1, 2, 3]))

    def test_pack_dynamic_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"a[8*]:=""\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1 + 8)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value("Hi"), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 1 + 2)
        self.assertEqual(buf[0], 2)
        self.assertEqual(buf[1:3], bytearray(b"Hi"))


class TestVMPackRecord(unittest.TestCase):

    def test_pack_record_u16_u8(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"{"U16"S"U8"C}:={0, 0}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(3)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value({"U16": 0x1234, "U8": 0x56}), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 3)
        self.assertEqual(buf, bytearray([0x34, 0x12, 0x56]))

    def test_pack_record_with_dynamic_string_and_status(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"{"Name"a[8*]"Status"L}:={"", 0}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(1 + 8 + 4)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value({"Name": "Hi", "Status": 0x12345678}), apx_base.NO_ERROR)
        self.assertEqual(vm.bytes_written(), 13)
        self.assertEqual(buf[0], 2)
        self.assertEqual(buf[1:3], bytearray(b"Hi"))
        self.assertEqual(buf[3:9], bytearray([0] * 6))
        self.assertEqual(buf[9:13], bytearray([0x78, 0x56, 0x34, 0x12]))

    def test_pack_record_with_range_check(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"{"Val"C(10, 50)}:={10}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)

        buf = bytearray(1)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value({"Val": 30}), apx_base.NO_ERROR)
        self.assertEqual(buf, bytearray([30]))

        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(vm.pack_value({"Val": 100}), apx_base.VALUE_RANGE_ERROR)


class TestVMPackRecordArray(unittest.TestCase):

    def test_pack_array_of_records(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"{"U16"S"U8"C}[2]:={{0, 0}, {0, 0}}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray(6)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(
            vm.pack_value([
                {"U16": 0x0102, "U8": 0x03},
                {"U16": 0x0405, "U8": 0x06},
            ]),
            apx_base.NO_ERROR
        )
        self.assertEqual(vm.bytes_written(), 6)
        self.assertEqual(buf, bytearray([0x02, 0x01, 0x03, 0x05, 0x04, 0x06]))

    def test_pack_array_of_records_with_dynamic_string(self):
        program = compile_port('APX/1.3\n'
                               'N"TestNode"\n'
                               'P"Signal"{"Label"a[4*]"Id"C}[2]:={{"", 0}, {"", 0}}\n')
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(program), apx_base.NO_ERROR)
        buf = bytearray((1 + 4 + 1) * 2)
        self.assertEqual(vm.set_write_buffer(buf), apx_base.NO_ERROR)
        self.assertEqual(
            vm.pack_value([
                {"Label": "Cat", "Id": 10},
                {"Label": "A", "Id": 20},
            ]),
            apx_base.NO_ERROR
        )
        self.assertEqual(vm.bytes_written(), 12)
        self.assertEqual(buf[0], 3)
        self.assertEqual(buf[1:4], bytearray(b"Cat"))
        self.assertEqual(buf[4:5], bytearray([0]))
        self.assertEqual(buf[5], 10)
        self.assertEqual(buf[6], 1)
        self.assertEqual(buf[7:8], bytearray(b"A"))
        self.assertEqual(buf[8:11], bytearray([0, 0, 0]))
        self.assertEqual(buf[11], 20)


class TestVMPackErrorHandling(unittest.TestCase):

    def test_pack_with_unpack_program_fails(self):
        unpack_program = compile_port('APX/1.3\n'
                                      'N"TestNode"\n'
                                      'R"Signal"C\n', is_pack=False)
        vm = apx.vm.VirtualMachine()
        self.assertEqual(vm.select_program(unpack_program), apx_base.NO_ERROR)
        buf = bytearray(1)
        vm.set_write_buffer(buf)
        self.assertEqual(vm.pack_value(10), apx_base.INVALID_PROGRAM_ERROR)

    def test_pack_without_program_fails(self):
        vm = apx.vm.VirtualMachine()
        buf = bytearray(1)
        vm.set_write_buffer(buf)
        self.assertEqual(vm.pack_value(10), apx_base.INVALID_PROGRAM_ERROR)


if __name__ == '__main__':
    unittest.main()
