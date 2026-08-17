"""
Unit tests for VM Program encoder
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base
import apx.vm.base
from apx.vm.program import Program


class TestVMProgram(unittest.TestCase):

    def test_encode_instruction_pack_uint8(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.UINT8, False)
        self.assertEqual(0b0, program.buffer[0])

    def test_encode_instruction_pack_uint16(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.UINT16, False)
        self.assertEqual(0b1, program.buffer[0])

    def test_encode_instruction_pack_uint32(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.UINT32, False)
        self.assertEqual(0b10, program.buffer[0])

    def test_encode_instruction_pack_uint64(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.UINT64, False)
        self.assertEqual(0b11, program.buffer[0])

    def test_encode_instruction_pack_uint8_array(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.UINT8, True)
        self.assertEqual(0b10000000, program.buffer[0])

    def test_encode_instruction_pack_record(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.RECORD, False)
        self.assertEqual(0b00001010, program.buffer[0])

    def test_encode_instruction_pack_record_array(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.PACK, apx.vm.base.Variant.RECORD, True)
        self.assertEqual(0b10001010, program.buffer[0])

    def test_encode_instruction_unpack_uint8(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.UINT8, False)
        self.assertEqual(0b10000, program.buffer[0])

    def test_encode_instruction_unpack_uint16(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.UINT16, False)
        self.assertEqual(0b10001, program.buffer[0])

    def test_encode_instruction_unpack_uint32(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.UINT32, False)
        self.assertEqual(0b10010, program.buffer[0])

    def test_encode_instruction_unpack_uint64(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.UINT64, False)
        self.assertEqual(0b10011, program.buffer[0])

    def test_encode_instruction_unpack_uint8_array(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.UINT8, True)
        self.assertEqual(0b10010000, program.buffer[0])

    def test_encode_instruction_unpack_record(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.RECORD, False)
        self.assertEqual(0b00011010, program.buffer[0])

    def test_encode_instruction_unpack_record_array(self):
        program = Program()
        program.encode_instruction(apx.vm.base.ProgramType.UNPACK, apx.vm.base.Variant.RECORD, True)
        self.assertEqual(0b10011010, program.buffer[0])

    def test_encode_uint8_array_size(self):
        program = Program()
        program.encode_array_size(10, False)
        expected = bytes([0b00100000, 10])
        self.assertEqual(program.buffer, expected)

    def test_encode_limit_values_uint8(self):
        program = Program()
        variant = apx.vm.base.Variant.LIMIT_CHECK_UINT8
        self.assertEqual(
            program.encode_limit_check_instruction(variant, 0, 255, is_array=False),
            apx_base.NO_ERROR)
        opcode_val = apx.vm.base.OpCode.DATA_CTRL.value << apx.vm.base.INSTR_OPCODE_SHIFT
        self.assertEqual(program.buffer, bytes([
            variant.value | opcode_val,
            0,
            255,
        ]))

    def test_encode_simple_pack_program_header(self):
        program = Program()
        self.assertEqual(
            program.encode_program_header(apx.vm.base.ProgramType.PACK, apx.vm.base.UINT8_SIZE, 0, False),
            apx_base.NO_ERROR)
        self.assertEqual(program.header, bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG,
            apx.vm.base.UINT8_SIZE
        ]))
