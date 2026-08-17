"""
APX byte code program encoder and utilities
"""
from __future__ import annotations
from struct import Struct
import apx.base as apx_base
import apx.vm.base as apx_vm_base

u8_struct = Struct("B")
u16_struct = Struct("<H")
u32_struct = Struct("<L")
u64_struct = Struct("<Q")
s8_struct = Struct("b")
s16_struct = Struct("<h")
s32_struct = Struct("<l")
s64_struct = Struct("<q")


def calc_data_variant(data_size: int) -> apx_vm_base.Variant:
    """
    Calculates the appropriate Variant for a given data size in bytes.
    """
    if data_size <= apx_vm_base.UINT8_MAX:
        return apx_vm_base.Variant.UINT8
    elif data_size <= apx_vm_base.UINT16_MAX:
        return apx_vm_base.Variant.UINT16
    elif data_size <= apx_vm_base.UINT32_MAX:
        return apx_vm_base.Variant.UINT32
    else:
        raise ValueError('Large value not supported')


def get_size_by_variant(variant: apx_vm_base.Variant) -> int:
    """
    Returns the byte size corresponding to a size variant.
    """
    if variant == apx_vm_base.Variant.UINT8:
        return apx_vm_base.UINT8_SIZE
    elif variant == apx_vm_base.Variant.UINT16:
        return apx_vm_base.UINT16_SIZE
    elif variant == apx_vm_base.Variant.UINT32:
        return apx_vm_base.UINT32_SIZE
    else:
        raise ValueError(variant)


def get_struct_by_variant(variant: apx_vm_base.Variant) -> Struct:
    """
    Returns the Struct packer for a given size variant.
    """
    if variant == apx_vm_base.Variant.UINT8:
        return u8_struct
    elif variant == apx_vm_base.Variant.UINT16:
        return u16_struct
    elif variant == apx_vm_base.Variant.UINT32:
        return u32_struct
    elif variant == apx_vm_base.Variant.UINT64:
        return u64_struct
    else:
        raise NotImplementedError(variant)


def calc_data_size_variant(elem_variant: apx_vm_base.Variant,
                           queue_variant: apx_vm_base.Variant) -> apx_vm_base.Variant:
    """
    Calculates the combined data size variant for queued elements.
    """
    if elem_variant == apx_vm_base.Variant.UINT8:
        data_size_variant = apx_vm_base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT8.value + queue_variant.value
    elif elem_variant == apx_vm_base.Variant.UINT16:
        data_size_variant = apx_vm_base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT16.value + queue_variant.value
    elif elem_variant == apx_vm_base.Variant.UINT32:
        data_size_variant = apx_vm_base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT32.value + queue_variant.value
    else:
        raise ValueError(elem_variant)
    return apx_vm_base.Variant(data_size_variant)


def calc_value_to_size_type(value: int) -> apx_vm_base.SizeType:
    """
    Utility method to convert array and queue lengths into SizeType enums
    """
    num_bits = value.bit_length()
    if value > 0 and num_bits > 0:
        if num_bits <= 8:
            return apx_vm_base.SizeType.UINT8
        elif num_bits <= 16:
            return apx_vm_base.SizeType.UINT16
        elif num_bits <= 32:
            return apx_vm_base.SizeType.UINT32
        else:
            # Number is too large for APX standard
            return apx_vm_base.SizeType.UNSUPPORTED
    return apx_vm_base.SizeType.NONE


def calc_size_type_to_size(size_type: apx_vm_base.SizeType) -> int:
    """
    Utility method to calculate how many bytes are needed to represent
    given size_type.
    Returns 0 on failure.
    """
    if size_type == apx_vm_base.SizeType.UINT8:
        return apx_vm_base.UINT8_SIZE
    elif size_type == apx_vm_base.SizeType.UINT16:
        return apx_vm_base.UINT16_SIZE
    elif size_type == apx_vm_base.SizeType.UINT32:
        return apx_vm_base.UINT32_SIZE
    else:
        return 0


class Encoder:
    """
    Encoder and container for APX VM byte code programs and headers.
    """

    def __init__(self) -> None:
        self.header: bytearray = bytearray()
        self.buffer: bytearray = bytearray()
        self.last_type_code: apx_base.TypeCode = apx_base.TypeCode.NONE

    def encode_instruction(self, opcode: apx_vm_base.OpCode, variant: apx_vm_base.Variant,
                           flag: bool) -> apx_base.Result:
        """
        Encodes a general VM instruction into the program buffer.
        """
        if opcode in (apx_vm_base.OpCode.PACK, apx_vm_base.OpCode.UNPACK):
            self.last_type_code = variant_to_type_code(variant)
        else:
            self.last_type_code = apx_base.TypeCode.NONE
        variant_part = variant.value & apx_vm_base.INSTR_VARIANT_MASK
        opcode_part = (opcode.value & apx_vm_base.INSTR_OPCODE_MASK) << apx_vm_base.INSTR_OPCODE_SHIFT
        result = variant_part | opcode_part
        if flag:
            result |= apx_vm_base.INSTR_FLAG
        self.buffer.append(result)
        return apx_base.NO_ERROR

    def encode_header_instruction(self, opcode: apx_vm_base.OpCode, variant: apx_vm_base.Variant,
                                  flag: bool) -> apx_base.Result:
        """
        Encodes an instruction into the program header.
        """
        variant_part = variant.value & apx_vm_base.INSTR_VARIANT_MASK
        opcode_part = (opcode.value & apx_vm_base.INSTR_OPCODE_MASK) << apx_vm_base.INSTR_OPCODE_SHIFT
        result = variant_part | opcode_part
        if flag:
            result |= apx_vm_base.INSTR_FLAG
        self.header.append(result)
        return apx_base.NO_ERROR

    def encode_array_size(self, array_size: int, is_dynamic: bool) -> apx_base.Result:
        """
        Encodes array size information into the program buffer.
        """
        opcode = apx_vm_base.OpCode.DATA_SIZE
        if array_size >= apx_vm_base.UINT32_MAX:
            return apx_base.LENGTH_ERROR
        elif array_size >= apx_vm_base.UINT16_MAX:
            variant = apx_vm_base.Variant.UINT32
            encoded_size = u32_struct.pack(array_size)
        elif array_size >= apx_vm_base.UINT8_MAX:
            variant = apx_vm_base.Variant.UINT16
            encoded_size = u16_struct.pack(array_size)
        else:
            variant = apx_vm_base.Variant.UINT8
            encoded_size = u8_struct.pack(array_size)
        self.encode_instruction(opcode, variant, is_dynamic)
        self.buffer.extend(encoded_size)
        return apx_base.NO_ERROR

    def encode_limit_check_instruction(self, variant: apx_vm_base.Variant,
                                       lower_limit: int, upper_limit: int,
                                       is_array: bool = False) -> apx_base.Result:
        """
        Encodes a limit check instruction and values into the program buffer.
        """
        if self.last_type_code == apx_base.TypeCode.BOOL:
            return apx_base.INVALID_INSTRUCTION_ERROR
        if variant.value < apx_vm_base.Variant.LIMIT_CHECK_UINT8.value:
            return apx_base.INVALID_INSTRUCTION_ERROR
        if variant.value > apx_vm_base.Variant.LIMIT_CHECK_LAST.value:
            return apx_base.INVALID_INSTRUCTION_ERROR
        self.encode_instruction(apx_vm_base.OpCode.DATA_CTRL, variant, is_array)
        return self.encode_limit_values(variant, lower_limit, upper_limit)

    def encode_limit_values(self, limit_variant: apx_vm_base.Variant,
                            lower_limit: int, upper_limit: int) -> apx_base.Result:
        """
        Encodes lower and upper limits into the program buffer.
        """
        if limit_variant == apx_vm_base.Variant.LIMIT_CHECK_UINT8:
            elem_size = apx_vm_base.UINT8_SIZE
            struct = u8_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_UINT16:
            elem_size = apx_vm_base.UINT16_SIZE
            struct = u16_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_UINT32:
            elem_size = apx_vm_base.UINT32_SIZE
            struct = u32_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_UINT64:
            elem_size = apx_vm_base.UINT64_SIZE
            struct = u64_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_INT8:
            elem_size = apx_vm_base.INT8_SIZE
            struct = s8_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_INT16:
            elem_size = apx_vm_base.INT16_SIZE
            struct = s16_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_INT32:
            elem_size = apx_vm_base.INT32_SIZE
            struct = s32_struct
        elif limit_variant == apx_vm_base.Variant.LIMIT_CHECK_INT64:
            elem_size = apx_vm_base.INT64_SIZE
            struct = s64_struct
        else:
            return apx_base.INVALID_INSTRUCTION_ERROR
        data = bytearray(elem_size * 2)
        struct.pack_into(data, 0, lower_limit)
        struct.pack_into(data, elem_size, upper_limit)
        self.buffer.extend(data)
        return apx_base.NO_ERROR

    def encode_program_header(self, program_type: apx_vm_base.ProgramType,
                              elem_size: int, queue_size: int, is_dynamic: bool) -> apx_base.Result:
        """
        Encodes the full APX program header.
        """
        self.header.extend([apx_vm_base.MAJOR_VERSION, apx_vm_base.MINOR_VERSION])
        is_queued = queue_size > 0
        if is_queued:
            try:
                queue_variant = calc_data_variant(queue_size)
                elem_variant = calc_data_variant(elem_size)
                queue_size_bytes = get_size_by_variant(queue_variant)
                data_size_variant = calc_data_size_variant(elem_variant, queue_variant)
            except ValueError:
                return apx_base.VALUE_TYPE_ERROR
            max_data_size = queue_size_bytes + elem_size * queue_size
            if max_data_size > apx_vm_base.UINT32_MAX:
                return apx_base.LENGTH_ERROR
        else:
            max_data_size = elem_size
        try:
            max_data_size_variant = calc_data_variant(max_data_size)
        except ValueError:
            return apx_base.VALUE_TYPE_ERROR
        self.encode_program_type_byte(program_type, max_data_size_variant, is_dynamic, is_queued)
        struct = get_struct_by_variant(max_data_size_variant)
        self.header.extend(struct.pack(max_data_size))
        if is_queued:
            self.encode_header_instruction(apx_vm_base.OpCode.DATA_SIZE, data_size_variant, False)
            struct = get_struct_by_variant(elem_variant)
            self.header.extend(struct.pack(elem_size))
        return apx_base.NO_ERROR

    def encode_program_type_byte(
            self, program_type: apx_vm_base.ProgramType, data_size_variant: apx_vm_base.Variant,
            is_dynamic: bool, is_queued: bool) -> None:
        """
        Encodes the program type and flags byte in the header.
        """
        value = data_size_variant.value & apx_vm_base.HEADER_DATA_SIZE_VARIANT_MASK
        if program_type == apx_vm_base.ProgramType.PACK:
            value |= apx_vm_base.HEADER_FLAG_PACK_PROG
        if is_dynamic:
            value |= apx_vm_base.HEADER_FLAG_DYNAMIC_DATA
        if is_queued:
            value |= apx_vm_base.HEADER_FLAG_QUEUED_DATA
        self.header.append(value)

    def encode_field_name(self, name: str) -> apx_base.Result:
        """
        Encodes a null-terminated field name string into the program buffer.
        """
        try:
            self.buffer.extend(bytes(name, 'ascii'))
        except UnicodeEncodeError:
            return apx_base.INVALID_NAME_ERROR
        self.buffer.append(0)  # Null-terminator
        return apx_base.NO_ERROR


VARIANT_TO_TYPE_CODE_MAP = {
    apx_vm_base.Variant.UINT8: apx_base.TypeCode.UINT8,
    apx_vm_base.Variant.UINT16: apx_base.TypeCode.UINT16,
    apx_vm_base.Variant.UINT32: apx_base.TypeCode.UINT32,
    apx_vm_base.Variant.UINT64: apx_base.TypeCode.UINT64,
    apx_vm_base.Variant.INT8: apx_base.TypeCode.INT8,
    apx_vm_base.Variant.INT16: apx_base.TypeCode.INT16,
    apx_vm_base.Variant.INT32: apx_base.TypeCode.INT32,
    apx_vm_base.Variant.INT64: apx_base.TypeCode.INT64,
    apx_vm_base.Variant.BOOL: apx_base.TypeCode.BOOL,
    apx_vm_base.Variant.BYTE: apx_base.TypeCode.BYTE,
    apx_vm_base.Variant.RECORD: apx_base.TypeCode.RECORD,
    apx_vm_base.Variant.CHAR: apx_base.TypeCode.CHAR,
    apx_vm_base.Variant.CHAR8: apx_base.TypeCode.CHAR8,
    apx_vm_base.Variant.CHAR16: apx_base.TypeCode.CHAR16,
    apx_vm_base.Variant.CHAR32: apx_base.TypeCode.CHAR32,
}


def variant_to_type_code(variant: apx_vm_base.Variant) -> apx_base.TypeCode:
    """
    Maps an instruction variant to the corresponding TypeCode.
    """
    return VARIANT_TO_TYPE_CODE_MAP.get(variant, apx_base.TypeCode.NONE)


def decode_instruction(instruction: int) -> tuple[apx_vm_base.OpCode, apx_vm_base.Variant, bool]:
    """
    Decodes an 8-bit instruction byte into (opcode, variant, flag).
    """
    flag = bool(instruction & apx_vm_base.INSTR_FLAG)
    opcode_val = (instruction >> apx_vm_base.INSTR_OPCODE_SHIFT) & apx_vm_base.INSTR_OPCODE_MASK
    variant_val = instruction & apx_vm_base.INSTR_VARIANT_MASK
    return apx_vm_base.OpCode(opcode_val), apx_vm_base.Variant(variant_val), flag


class Decoder:
    """
    APX VM 2.1 bytecode program decoder and iterator.
    """

    def __init__(self) -> None:
        self.program: bytes = b""
        self.read_pos: int = 0
        self.mark_pos: int | None = None
        self.last_type_code: apx_base.TypeCode = apx_base.TypeCode.NONE
        self.operation_type: apx_vm_base.OperationType = apx_vm_base.OperationType.PROGRAM_END
        self.pack_unpack_info: apx_vm_base.PackUnpackOperationInfo = (
            apx_vm_base.PackUnpackOperationInfo(apx_base.TypeCode.NONE, 0, False)
        )
        self.range_check_info: apx_vm_base.RangeCheckOperationInfo = (
            apx_vm_base.RangeCheckOperationInfo(0, 0)
        )
        self.field_name: str = ""
        self.is_first_field: bool = False
        self.is_array_limit: bool = False

    def select_program(self, program: bytes | bytearray | memoryview) -> apx_base.Result:
        """
        Selects a bytecode program for decoding and resets the read position.
        """
        if program is None:
            return apx_base.NULL_PTR_ERROR
        self.program = bytes(program)
        self.read_pos = 0
        self.mark_pos = None
        self.last_type_code = apx_base.TypeCode.NONE
        self.operation_type = apx_vm_base.OperationType.PROGRAM_END
        self.pack_unpack_info = apx_vm_base.PackUnpackOperationInfo(apx_base.TypeCode.NONE, 0, False)
        self.range_check_info = apx_vm_base.RangeCheckOperationInfo(0, 0)
        self.field_name = ""
        self.is_first_field = False
        self.is_array_limit = False
        return apx_base.NO_ERROR

    def parse_program_header(self) -> tuple[apx_base.Result, apx_vm_base.ProgramHeader | None]:
        """
        Parses and validates the APX VM 2.1 program header, advancing the read position.
        """
        if len(self.program) < self.read_pos + 4:
            return apx_base.PARSE_ERROR, None
        if self.program[self.read_pos] != apx_vm_base.MAJOR_VERSION:
            return apx_base.INVALID_HEADER_ERROR, None
        if self.program[self.read_pos + 1] != apx_vm_base.MINOR_VERSION:
            return apx_base.INVALID_HEADER_ERROR, None

        type_byte = self.program[self.read_pos + 2]
        data_size_variant_val = type_byte & apx_vm_base.HEADER_DATA_SIZE_VARIANT_MASK
        program_type = (apx_vm_base.ProgramType.PACK
                        if (type_byte & apx_vm_base.HEADER_FLAG_PACK_PROG)
                        else apx_vm_base.ProgramType.UNPACK)
        is_dynamic = bool(type_byte & apx_vm_base.HEADER_FLAG_DYNAMIC_DATA)
        is_queued = bool(type_byte & apx_vm_base.HEADER_FLAG_QUEUED_DATA)
        self.read_pos += 3

        size_structs = {
            apx_vm_base.Variant.UINT8.value: (u8_struct, 1),
            apx_vm_base.Variant.UINT16.value: (u16_struct, 2),
            apx_vm_base.Variant.UINT32.value: (u32_struct, 4),
        }
        if data_size_variant_val not in size_structs:
            return apx_base.INVALID_HEADER_ERROR, None

        st, size_bytes = size_structs[data_size_variant_val]
        if self.read_pos + size_bytes > len(self.program):
            return apx_base.PARSE_ERROR, None
        max_data_size = st.unpack_from(self.program, self.read_pos)[0]
        self.read_pos += size_bytes

        element_size = 0
        queue_length = 0
        if is_queued:
            rc, element_size, queue_length = self._parse_queued_header(max_data_size)
            if rc != apx_base.NO_ERROR:
                return rc, None

        header = apx_vm_base.ProgramHeader(
            program_type, max_data_size, is_dynamic, is_queued, element_size, queue_length
        )
        return apx_base.NO_ERROR, header

    def _parse_queued_header(self, max_data_size: int) -> tuple[apx_base.Result, int, int]:
        if self.read_pos >= len(self.program):
            return apx_base.PARSE_ERROR, 0, 0
        instr = self.program[self.read_pos]
        self.read_pos += 1
        try:
            opcode, variant, _ = decode_instruction(instr)
        except ValueError:
            return apx_base.PARSE_ERROR, 0, 0
        if opcode != apx_vm_base.OpCode.DATA_SIZE or variant.value < 3 or variant.value > 11:
            return apx_base.PARSE_ERROR, 0, 0

        if 3 <= variant.value <= 5:
            elem_size_bytes, elem_struct = 1, u8_struct
            queue_storage_size = 1 if variant.value == 3 else (2 if variant.value == 4 else 4)
        elif 6 <= variant.value <= 8:
            elem_size_bytes, elem_struct = 2, u16_struct
            queue_storage_size = 1 if variant.value == 6 else (2 if variant.value == 7 else 4)
        else:  # 9 <= variant.value <= 11
            elem_size_bytes, elem_struct = 4, u32_struct
            queue_storage_size = 1 if variant.value == 9 else (2 if variant.value == 10 else 4)

        if self.read_pos + elem_size_bytes > len(self.program):
            return apx_base.PARSE_ERROR, 0, 0
        element_size = elem_struct.unpack_from(self.program, self.read_pos)[0]
        self.read_pos += elem_size_bytes

        if element_size == 0 or max_data_size < queue_storage_size:
            return apx_base.PARSE_ERROR, 0, 0
        rem = max_data_size - queue_storage_size
        if rem % element_size != 0:
            return apx_base.INVALID_HEADER_ERROR, 0, 0
        queue_length = rem // element_size
        return apx_base.NO_ERROR, element_size, queue_length

    def parse_next_operation(self) -> tuple[apx_base.Result, apx_vm_base.OperationType]:
        """
        Decodes the next instruction and associated payloads from the program.
        """
        if self.read_pos >= len(self.program):
            self.operation_type = apx_vm_base.OperationType.PROGRAM_END
            return apx_base.NO_ERROR, apx_vm_base.OperationType.PROGRAM_END

        instruction = self.program[self.read_pos]
        self.read_pos += 1
        try:
            opcode, variant, flag = decode_instruction(instruction)
        except ValueError:
            return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END

        if opcode in (apx_vm_base.OpCode.PACK, apx_vm_base.OpCode.UNPACK):
            return self._decode_pack_unpack(opcode, variant, flag)
        elif opcode == apx_vm_base.OpCode.DATA_CTRL:
            return self._decode_data_ctrl(variant, flag)
        elif opcode == apx_vm_base.OpCode.FLOW_CTRL:
            self.last_type_code = apx_base.TypeCode.NONE
            if variant == apx_vm_base.Variant.ARRAY_NEXT:
                self.operation_type = apx_vm_base.OperationType.ARRAY_NEXT
                return apx_base.NO_ERROR, apx_vm_base.OperationType.ARRAY_NEXT
            return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END
        return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END

    def _decode_array_size(self) -> tuple[apx_base.Result, int, bool]:
        if self.read_pos >= len(self.program):
            return apx_base.UNEXPECTED_END_ERROR, 0, False
        size_instr = self.program[self.read_pos]
        self.read_pos += 1
        try:
            size_opcode, size_variant, is_dynamic = decode_instruction(size_instr)
        except ValueError:
            return apx_base.INVALID_INSTRUCTION_ERROR, 0, False

        if size_opcode != apx_vm_base.OpCode.DATA_SIZE:
            return apx_base.INVALID_INSTRUCTION_ERROR, 0, False
        if size_variant.value > apx_vm_base.Variant.ARRAY_SIZE_LAST.value:
            return apx_base.INVALID_INSTRUCTION_ERROR, 0, False

        size_map = {
            apx_vm_base.Variant.ARRAY_SIZE_UINT8: (u8_struct, 1),
            apx_vm_base.Variant.ARRAY_SIZE_UINT16: (u16_struct, 2),
            apx_vm_base.Variant.ARRAY_SIZE_UINT32: (u32_struct, 4),
        }
        st, size_bytes = size_map[size_variant]
        if self.read_pos + size_bytes > len(self.program):
            return apx_base.UNEXPECTED_END_ERROR, 0, False
        array_len = st.unpack_from(self.program, self.read_pos)[0]
        self.read_pos += size_bytes
        return apx_base.NO_ERROR, array_len, is_dynamic

    def _decode_pack_unpack(self, opcode: apx_vm_base.OpCode, variant: apx_vm_base.Variant,
                            flag: bool) -> tuple[apx_base.Result, apx_vm_base.OperationType]:
        type_code = variant_to_type_code(variant)
        if type_code == apx_base.TypeCode.NONE:
            return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END
        self.last_type_code = type_code

        if flag:
            rc, array_len, is_dynamic = self._decode_array_size()
            if rc != apx_base.NO_ERROR:
                return rc, apx_vm_base.OperationType.PROGRAM_END
            self.pack_unpack_info = apx_vm_base.PackUnpackOperationInfo(type_code, array_len, is_dynamic)
        else:
            self.pack_unpack_info = apx_vm_base.PackUnpackOperationInfo(type_code, 0, False)

        op_type = (apx_vm_base.OperationType.PACK
                   if opcode == apx_vm_base.OpCode.PACK
                   else apx_vm_base.OperationType.UNPACK)
        self.operation_type = op_type
        return apx_base.NO_ERROR, op_type

    def _decode_data_ctrl(self, variant: apx_vm_base.Variant,
                          flag: bool) -> tuple[apx_base.Result, apx_vm_base.OperationType]:
        if variant == apx_vm_base.Variant.RECORD_SELECT:
            self.last_type_code = apx_base.TypeCode.NONE
            self.is_first_field = flag
            null_pos = self.program.find(b'\x00', self.read_pos)
            if null_pos == -1:
                return apx_base.UNEXPECTED_END_ERROR, apx_vm_base.OperationType.PROGRAM_END
            try:
                self.field_name = str(self.program[self.read_pos:null_pos], 'ascii')
            except UnicodeDecodeError:
                return apx_base.INVALID_NAME_ERROR, apx_vm_base.OperationType.PROGRAM_END
            self.read_pos = null_pos + 1
            self.operation_type = apx_vm_base.OperationType.RECORD_SELECT
            return apx_base.NO_ERROR, apx_vm_base.OperationType.RECORD_SELECT

        if variant == apx_vm_base.Variant.RECORD_END:
            self.last_type_code = apx_base.TypeCode.NONE
            self.operation_type = apx_vm_base.OperationType.RECORD_END
            return apx_base.NO_ERROR, apx_vm_base.OperationType.RECORD_END

        if apx_vm_base.Variant.LIMIT_CHECK_UINT8.value <= variant.value <= apx_vm_base.Variant.LIMIT_CHECK_LAST.value:
            if self.last_type_code == apx_base.TypeCode.BOOL:
                return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END
            self.last_type_code = apx_base.TypeCode.NONE
            return self._decode_limit_check(variant, flag)

        return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END

    def _decode_limit_check(self, variant: apx_vm_base.Variant,
                            flag: bool) -> tuple[apx_base.Result, apx_vm_base.OperationType]:
        self.is_array_limit = flag
        limit_map = {
            apx_vm_base.Variant.LIMIT_CHECK_UINT8: (u8_struct, 1, apx_vm_base.OperationType.LIMIT_CHECK_UINT8),
            apx_vm_base.Variant.LIMIT_CHECK_UINT16: (u16_struct, 2, apx_vm_base.OperationType.LIMIT_CHECK_UINT16),
            apx_vm_base.Variant.LIMIT_CHECK_UINT32: (u32_struct, 4, apx_vm_base.OperationType.LIMIT_CHECK_UINT32),
            apx_vm_base.Variant.LIMIT_CHECK_UINT64: (u64_struct, 8, apx_vm_base.OperationType.LIMIT_CHECK_UINT64),
            apx_vm_base.Variant.LIMIT_CHECK_INT8: (s8_struct, 1, apx_vm_base.OperationType.LIMIT_CHECK_INT8),
            apx_vm_base.Variant.LIMIT_CHECK_INT16: (s16_struct, 2, apx_vm_base.OperationType.LIMIT_CHECK_INT16),
            apx_vm_base.Variant.LIMIT_CHECK_INT32: (s32_struct, 4, apx_vm_base.OperationType.LIMIT_CHECK_INT32),
            apx_vm_base.Variant.LIMIT_CHECK_INT64: (s64_struct, 8, apx_vm_base.OperationType.LIMIT_CHECK_INT64),
        }
        if variant not in limit_map:
            return apx_base.INVALID_INSTRUCTION_ERROR, apx_vm_base.OperationType.PROGRAM_END
        st, size, op_type = limit_map[variant]
        if self.read_pos + (size * 2) > len(self.program):
            return apx_base.UNEXPECTED_END_ERROR, apx_vm_base.OperationType.PROGRAM_END
        lower = st.unpack_from(self.program, self.read_pos)[0]
        upper = st.unpack_from(self.program, self.read_pos + size)[0]
        self.read_pos += size * 2
        self.range_check_info = apx_vm_base.RangeCheckOperationInfo(lower, upper)
        self.operation_type = op_type
        return apx_base.NO_ERROR, op_type

    def save_program_position(self) -> None:
        """
        Saves current read position in the program.
        """
        self.mark_pos = self.read_pos

    def recall_program_position(self) -> None:
        """
        Recalls previously saved program position.
        """
        if self.mark_pos is not None:
            self.read_pos = self.mark_pos

    def has_saved_program_position(self) -> bool:
        """
        Returns True if a program position has been saved.
        """
        return self.mark_pos is not None
