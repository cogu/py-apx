from struct import Struct
import apx.base as apx_base
import apx.vm.base

u8_struct = Struct("B")
u16_struct = Struct("<H")
u32_struct = Struct("<L")
u64_struct = Struct("<Q")
s8_struct = Struct("b")
s16_struct = Struct("<h")
s32_struct = Struct("<l")
s64_struct = Struct("<q")


def calc_data_variant(data_size: int) -> apx.vm.base.Variant:
    if data_size <= apx.vm.base.UINT8_MAX:
        return apx.vm.base.Variant.UINT8
    elif data_size <= apx.vm.base.UINT16_MAX:
        return apx.vm.base.Variant.UINT16
    elif data_size <= apx.vm.base.UINT32_MAX:
        return apx.vm.base.Variant.UINT32
    else:
        raise ValueError('Large value not supported')


def get_size_by_variant(variant: apx.vm.base.Variant) -> int:
    if variant == apx.vm.base.Variant.UINT8:
        return apx.vm.base.UINT8_SIZE
    elif variant == apx.vm.base.Variant.UINT16:
        return apx.vm.base.UINT16_SIZE
    elif variant == apx.vm.base.Variant.UINT32:
        return apx.vm.base.UINT32_SIZE
    else:
        raise ValueError(variant)


def get_struct_by_variant(variant: apx.vm.base.Variant) -> Struct:
    if variant == apx.vm.base.Variant.UINT8:
        return u8_struct
    elif variant == apx.vm.base.Variant.UINT16:
        return u16_struct
    elif variant == apx.vm.base.Variant.UINT32:
        return u32_struct
    elif variant == apx.vm.base.Variant.UINT64:
        return u64_struct
    else:
        raise NotImplementedError(variant)


def calc_data_size_variant(elem_variant: apx.vm.base.Variant,
                           queue_variant: apx.vm.base.Variant) -> apx.vm.base.Variant:
    if elem_variant == apx.vm.base.Variant.UINT8:
        data_size_variant = apx.vm.base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT8.value + queue_variant.value
    elif elem_variant == apx.vm.base.Variant.UINT16:
        data_size_variant = apx.vm.base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT16.value + queue_variant.value
    elif elem_variant == apx.vm.base.Variant.UINT32:
        data_size_variant = apx.vm.base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT32.value + queue_variant.value
    else:
        raise ValueError(elem_variant)
    return apx.vm.base.Variant(data_size_variant)


def calc_value_to_size_type(value: int) -> apx.vm.base.SizeType:
    """
    Utility method to convert array and queue lengths into SizeType enums
    """
    num_bits = value.bit_length()
    if value > 0 and num_bits > 0:
        if num_bits <= 8:
            return apx.vm.base.SizeType.UINT8
        elif num_bits <= 16:
            return apx.vm.base.SizeType.UINT16
        elif num_bits <= 32:
            return apx.vm.base.SizeType.UINT32
        else:
            # Number is too large for APX standard
            return apx.vm.base.SizeType.UNSUPPORTED
    return apx.vm.base.SizeType.NONE  # TODO: CHANGE TO NONE


def calc_size_type_to_size(size_type: apx.vm.base.SizeType) -> int:
    """
    Utility method to calculate how many bytes are needed to represent
    given size_type.
    Returns 0 on failure.
    """
    if size_type == apx.vm.base.SizeType.UINT8:
        return apx.vm.base.UINT8_SIZE
    elif size_type == apx.vm.base.SizeType.UINT16:
        return apx.vm.base.UINT16_SIZE
    elif size_type == apx.vm.base.SizeType.UINT32:
        return apx.vm.base.UINT32_SIZE
    else:
        return 0


class Program:
    def __init__(self) -> None:
        self.header: bytearray = bytearray()
        self.buffer: bytearray = bytearray()

    def encode_instruction(self, opcode: apx.vm.base.OpCode, variant: apx.vm.base.Variant,
                           flag: bool) -> apx_base.Result:
        variant_part = variant.value & apx.vm.base.INSTR_VARIANT_MASK
        opcode_part = (opcode.value & apx.vm.base.INSTR_OPCODE_MASK) << apx.vm.base.INSTR_OPCODE_SHIFT
        result = variant_part | opcode_part
        if flag:
            result |= apx.vm.base.INSTR_FLAG
        self.buffer.append(result)
        return apx_base.NO_ERROR

    def encode_header_instruction(self, opcode: apx.vm.base.OpCode, variant: apx.vm.base.Variant,
                                  flag: bool) -> apx_base.Result:
        variant_part = variant.value & apx.vm.base.INSTR_VARIANT_MASK
        opcode_part = (opcode.value & apx.vm.base.INSTR_OPCODE_MASK) << apx.vm.base.INSTR_OPCODE_SHIFT
        result = variant_part | opcode_part
        if flag:
            result |= apx.vm.base.INSTR_FLAG
        self.header.append(result)
        return apx_base.NO_ERROR

    def encode_array_size(self, array_size: int, is_dynamic: bool) -> apx_base.Result:
        opcode = apx.vm.base.OpCode.DATA_SIZE
        if array_size >= apx.vm.base.UINT32_MAX:
            return apx_base.LENGTH_ERROR
        elif array_size >= apx.vm.base.UINT16_MAX:
            variant = apx.vm.base.Variant.UINT32
            encoded_size = u32_struct.pack(array_size)
        elif array_size >= apx.vm.base.UINT8_MAX:
            variant = apx.vm.base.Variant.UINT16
            encoded_size = u16_struct.pack(array_size)
        else:
            variant = apx.vm.base.Variant.UINT8
            encoded_size = u8_struct.pack(array_size)
        self.encode_instruction(opcode, variant, is_dynamic)
        self.buffer.extend(encoded_size)
        return apx_base.NO_ERROR

    def encode_limit_check_instruction(self, variant: apx.vm.base.Variant,
                                       lower_limit: int, upper_limit: int,
                                       is_array: bool) -> apx_base.Result:
        self.encode_instruction(apx.vm.base.OpCode.DATA_CTRL, variant, is_array)
        return self.encode_limit_values(variant, lower_limit, upper_limit)

    def encode_limit_values(self, limit_variant: apx.vm.base.Variant,
                            lower_limit: int, upper_limit: int) -> apx_base.Result:
        if limit_variant == apx.vm.base.Variant.LIMIT_CHECK_UINT8:
            elem_size = apx.vm.base.UINT8_SIZE
            struct = u8_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_UINT16:
            elem_size = apx.vm.base.UINT16_SIZE
            struct = u16_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_UINT32:
            elem_size = apx.vm.base.UINT32_SIZE
            struct = u32_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_UINT64:
            elem_size = apx.vm.base.UINT64_SIZE
            struct = u64_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_INT8:
            elem_size = apx.vm.base.INT8_SIZE
            struct = s8_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_INT16:
            elem_size = apx.vm.base.INT8_SIZE
            struct = s16_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_INT32:
            elem_size = apx.vm.base.INT8_SIZE
            struct = s32_struct
        elif limit_variant == apx.vm.base.Variant.LIMIT_CHECK_INT64:
            elem_size = apx.vm.base.INT8_SIZE
            struct = s64_struct
        else:
            raise NotImplementedError(limit_variant)
        data = bytearray(elem_size * 2)
        struct.pack_into(data, 0, lower_limit)
        struct.pack_into(data, elem_size, upper_limit)
        self.buffer.extend(data)
        return apx_base.NO_ERROR

    def encode_program_header(self, program_type: apx.vm.base.ProgramType,
                              elem_size: int, queue_size: int, is_dynamic: bool) -> apx_base.Result:
        self.header.extend([apx.vm.base.MAJOR_VERSION, apx.vm.base.MINOR_VERSION])
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
            if max_data_size > apx.vm.base.UINT32_MAX:
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
            self.encode_header_instruction(apx.vm.base.OpCode.DATA_SIZE, data_size_variant, False)
            struct = get_struct_by_variant(elem_variant)
            self.header.extend(struct.pack(elem_size))
        return apx_base.NO_ERROR

    def encode_program_type_byte(
            self, program_type: apx.vm.base.ProgramType, data_size_variant: apx.vm.base.Variant,
            is_dynamic: bool, is_queued: bool) -> None:
        value = (data_size_variant.value & apx.vm.base.HEADER_DATA_SIZE_VARIANT_MASK)
        if program_type == apx.vm.base.ProgramType.PACK:
            value |= apx.vm.base.HEADER_FLAG_PACK_PROG
        if is_dynamic:
            value |= apx.vm.base.HEADER_FLAG_DYNAMIC_DATA
        if is_queued:
            value |= apx.vm.base.HEADER_FLAG_QUEUED_DATA
        self.header.append(value)

    def encode_field_name(self, name: str) -> apx_base.Result:
        try:
            self.buffer.extend(bytes(name, 'ascii'))
        except UnicodeEncodeError:
            return apx_base.INVALID_NAME_ERROR
        self.buffer.append(0)  # Null-terminator
        return apx_base.NO_ERROR
