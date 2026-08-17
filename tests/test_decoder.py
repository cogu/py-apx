"""
Unit tests for VM Program decoder
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base
import apx.vm.base
from apx.vm.program import Encoder, Decoder


class TestDecoderHeader(unittest.TestCase):

    def test_parse_simple_pack_header_uint8(self):
        encoder = Encoder()
        self.assertEqual(
            encoder.encode_program_header(apx.vm.base.ProgramType.PACK, 10, 0, False),
            apx_base.NO_ERROR
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertIsNotNone(header)
        self.assertEqual(header.program_type, apx.vm.base.ProgramType.PACK)
        self.assertEqual(header.data_size, 10)
        self.assertFalse(header.is_dynamic)
        self.assertFalse(header.is_queued)
        self.assertEqual(header.element_size, 0)
        self.assertEqual(header.queue_length, 0)

    def test_parse_simple_unpack_header_uint16(self):
        encoder = Encoder()
        self.assertEqual(
            encoder.encode_program_header(apx.vm.base.ProgramType.UNPACK, 1000, 0, True),
            apx_base.NO_ERROR
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertIsNotNone(header)
        self.assertEqual(header.program_type, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(header.data_size, 1000)
        self.assertTrue(header.is_dynamic)
        self.assertFalse(header.is_queued)

    def test_parse_pack_header_uint32(self):
        encoder = Encoder()
        self.assertEqual(
            encoder.encode_program_header(apx.vm.base.ProgramType.PACK, 100000, 0, False),
            apx_base.NO_ERROR
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertIsNotNone(header)
        self.assertEqual(header.program_type, apx.vm.base.ProgramType.PACK)
        self.assertEqual(header.data_size, 100000)
        self.assertFalse(header.is_dynamic)
        self.assertFalse(header.is_queued)

    def test_parse_queued_port_header(self):
        encoder = Encoder()
        # elem_size = 4 (uint32 size), queue_size = 10 -> total data_size = 1 (queue prefix) + 4 * 10 = 41
        self.assertEqual(
            encoder.encode_program_header(apx.vm.base.ProgramType.PACK, 4, 10, False),
            apx_base.NO_ERROR
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertIsNotNone(header)
        self.assertEqual(header.program_type, apx.vm.base.ProgramType.PACK)
        self.assertEqual(header.data_size, 41)
        self.assertTrue(header.is_queued)
        self.assertEqual(header.element_size, 4)
        self.assertEqual(header.queue_length, 10)

    def test_parse_header_invalid_magic_or_version(self):
        invalid_header = bytes([0x00, 0x00, 0x00, 0x01])
        decoder = Decoder()
        self.assertEqual(decoder.select_program(invalid_header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.INVALID_HEADER_ERROR)
        self.assertIsNone(header)

    def test_parse_header_truncated(self):
        truncated_header = bytes([apx.vm.base.MAJOR_VERSION, apx.vm.base.MINOR_VERSION])
        decoder = Decoder()
        self.assertEqual(decoder.select_program(truncated_header), apx_base.NO_ERROR)
        rc, header = decoder.parse_program_header()
        self.assertEqual(rc, apx_base.PARSE_ERROR)
        self.assertIsNone(header)


class TestDecoderUInt8(unittest.TestCase):

    def test_unpack_scalar(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT8, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(decoder.pack_unpack_info.array_length, 0)
        self.assertFalse(decoder.pack_unpack_info.is_dynamic_array)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PROGRAM_END)

    def test_pack_scalar(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.UINT8, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(decoder.pack_unpack_info.array_length, 0)
        self.assertFalse(decoder.pack_unpack_info.is_dynamic_array)

    def test_unpack_fixed_array(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT8, True)
        encoder.encode_array_size(10, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(decoder.pack_unpack_info.array_length, 10)
        self.assertFalse(decoder.pack_unpack_info.is_dynamic_array)

    def test_pack_dynamic_array(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.UINT8, True)
        encoder.encode_array_size(500, True)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)
        self.assertEqual(decoder.pack_unpack_info.array_length, 500)
        self.assertTrue(decoder.pack_unpack_info.is_dynamic_array)

    def test_limit_check_scalar_and_array(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_UINT8, 0, 100, is_array=False)
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_UINT8, 5, 50, is_array=True)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_UINT8)
        self.assertEqual(decoder.range_check_info.lower_limit, 0)
        self.assertEqual(decoder.range_check_info.upper_limit, 100)
        self.assertFalse(decoder.is_array_limit)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_UINT8)
        self.assertEqual(decoder.range_check_info.lower_limit, 5)
        self.assertEqual(decoder.range_check_info.upper_limit, 50)
        self.assertTrue(decoder.is_array_limit)


class TestDecoderUInt16(unittest.TestCase):

    def test_pack_unpack_uint16(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.UINT16, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT16, True)
        encoder.encode_array_size(20, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT16)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT16)
        self.assertEqual(decoder.pack_unpack_info.array_length, 20)

    def test_limit_check_uint16(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_UINT16, 1000, 50000, is_array=False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_UINT16)
        self.assertEqual(decoder.range_check_info.lower_limit, 1000)
        self.assertEqual(decoder.range_check_info.upper_limit, 50000)


class TestDecoderUInt32(unittest.TestCase):

    def test_pack_unpack_uint32(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.UINT32, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT32, True)
        encoder.encode_array_size(100000, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT32)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT32)
        self.assertEqual(decoder.pack_unpack_info.array_length, 100000)

    def test_limit_check_uint32(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_UINT32, 10, 0x12345678, is_array=False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_UINT32)
        self.assertEqual(decoder.range_check_info.lower_limit, 10)
        self.assertEqual(decoder.range_check_info.upper_limit, 0x12345678)


class TestDecoderUInt64(unittest.TestCase):

    def test_pack_unpack_uint64(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.UINT64, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT64, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT64)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT64)

    def test_limit_check_uint64(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(
            apx.vm.base.Variant.LIMIT_CHECK_UINT64, 0, 0xFFFFFFFFFFFFFFFF, is_array=False
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_UINT64)
        self.assertEqual(decoder.range_check_info.lower_limit, 0)
        self.assertEqual(decoder.range_check_info.upper_limit, 0xFFFFFFFFFFFFFFFF)


class TestDecoderInt8(unittest.TestCase):

    def test_pack_unpack_int8(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.INT8, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.INT8, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT8)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT8)

    def test_limit_check_int8(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_INT8, -128, 127, is_array=False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_INT8)
        self.assertEqual(decoder.range_check_info.lower_limit, -128)
        self.assertEqual(decoder.range_check_info.upper_limit, 127)


class TestDecoderInt16(unittest.TestCase):

    def test_pack_unpack_int16(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.INT16, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.INT16, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT16)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT16)

    def test_limit_check_int16(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_INT16, -32000, 32000, is_array=False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_INT16)
        self.assertEqual(decoder.range_check_info.lower_limit, -32000)
        self.assertEqual(decoder.range_check_info.upper_limit, 32000)


class TestDecoderInt32(unittest.TestCase):

    def test_pack_unpack_int32(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.INT32, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.INT32, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT32)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT32)

    def test_limit_check_int32(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_INT32, -1000000, 1000000, is_array=False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_INT32)
        self.assertEqual(decoder.range_check_info.lower_limit, -1000000)
        self.assertEqual(decoder.range_check_info.upper_limit, 1000000)


class TestDecoderInt64(unittest.TestCase):

    def test_pack_unpack_int64(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.INT64, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.INT64, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT64)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.INT64)

    def test_limit_check_int64(self):
        encoder = Encoder()
        encoder.encode_limit_check_instruction(
            apx.vm.base.Variant.LIMIT_CHECK_INT64, -5000000000, 5000000000, is_array=False
        )
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.LIMIT_CHECK_INT64)
        self.assertEqual(decoder.range_check_info.lower_limit, -5000000000)
        self.assertEqual(decoder.range_check_info.upper_limit, 5000000000)


class TestDecoderBool(unittest.TestCase):

    def test_pack_unpack_bool(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.BOOL, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.BOOL, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.BOOL)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.BOOL)

    def test_limit_check_bool_rejected(self):
        # 1. Encoder rejects limit check after bool
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.BOOL, False)
        self.assertEqual(
            encoder.encode_limit_check_instruction(apx.vm.base.Variant.LIMIT_CHECK_UINT8, 0, 1),
            apx_base.INVALID_INSTRUCTION_ERROR
        )

        # 2. Decoder rejects limit check after bool
        raw_program = bytearray()
        opcode_pack = apx.vm.base.OpCode.PACK.value << apx.vm.base.INSTR_OPCODE_SHIFT
        pack_bool_byte = opcode_pack | apx.vm.base.Variant.BOOL.value
        opcode_ctrl = apx.vm.base.OpCode.DATA_CTRL.value << apx.vm.base.INSTR_OPCODE_SHIFT
        limit_check_byte = opcode_ctrl | apx.vm.base.Variant.LIMIT_CHECK_UINT8.value
        raw_program.append(pack_bool_byte)
        raw_program.append(limit_check_byte)
        raw_program.extend([0, 1])

        decoder = Decoder()
        self.assertEqual(decoder.select_program(raw_program), apx_base.NO_ERROR)
        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.BOOL)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.INVALID_INSTRUCTION_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PROGRAM_END)


class TestDecoderByte(unittest.TestCase):

    def test_pack_unpack_byte(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.BYTE, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.BYTE, True)
        encoder.encode_array_size(64, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.BYTE)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.BYTE)
        self.assertEqual(decoder.pack_unpack_info.array_length, 64)


class TestDecoderChar(unittest.TestCase):

    def test_pack_unpack_char_variants(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.CHAR, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.CHAR8, False)
        encoder.encode_instruction(apx.vm.base.OpCode.PACK, apx.vm.base.Variant.CHAR16, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.CHAR32, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.CHAR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.CHAR8)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.PACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.CHAR16)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.CHAR32)


class TestDecoderRecord(unittest.TestCase):

    def test_record_select_and_record_end(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.RECORD, False)
        encoder.encode_instruction(apx.vm.base.OpCode.DATA_CTRL, apx.vm.base.Variant.RECORD_SELECT, True)
        encoder.encode_field_name("Speed")
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT16, False)
        encoder.encode_instruction(apx.vm.base.OpCode.DATA_CTRL, apx.vm.base.Variant.RECORD_SELECT, False)
        encoder.encode_field_name("Status")
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT8, False)
        encoder.encode_instruction(apx.vm.base.OpCode.DATA_CTRL, apx.vm.base.Variant.RECORD_END, False)

        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.RECORD)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.RECORD_SELECT)
        self.assertEqual(decoder.field_name, "Speed")
        self.assertTrue(decoder.is_first_field)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT16)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.RECORD_SELECT)
        self.assertEqual(decoder.field_name, "Status")
        self.assertFalse(decoder.is_first_field)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.RECORD_END)

    def test_array_next(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.FLOW_CTRL, apx.vm.base.Variant.ARRAY_NEXT, False)
        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.ARRAY_NEXT)


class TestDecoderPosition(unittest.TestCase):

    def test_save_and_recall_program_position(self):
        encoder = Encoder()
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT8, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT16, False)
        encoder.encode_instruction(apx.vm.base.OpCode.UNPACK, apx.vm.base.Variant.UINT32, False)

        decoder = Decoder()
        self.assertEqual(decoder.select_program(encoder.buffer), apx_base.NO_ERROR)
        self.assertFalse(decoder.has_saved_program_position())

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT8)

        # Save position before UINT16
        decoder.save_program_position()
        self.assertTrue(decoder.has_saved_program_position())

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT16)

        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT32)

        # Recall position back to UINT16
        decoder.recall_program_position()
        rc, op_type = decoder.parse_next_operation()
        self.assertEqual(rc, apx_base.NO_ERROR)
        self.assertEqual(op_type, apx.vm.base.OperationType.UNPACK)
        self.assertEqual(decoder.pack_unpack_info.type_code, apx_base.TypeCode.UINT16)
