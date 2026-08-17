"""
APX data serializer
"""
import struct
from typing import Any
from collections import deque
import apx.base as apx_base

DYNAMIC_SIZE_STRUCT = [
    'B',  # UINT8
    'H',  # UINT16
    'L',  # UINT32
]


class ReadBuffer:
    """
    Write buffer wrapper
    """
    def __init__(self, data: bytearray | bytes) -> None:
        self.data = data
        self.read_pos = 0
        self.end_pos = len(data)
        self.padded_read_pos = None

    @property
    def is_valid(self) -> bool:
        """
        Returns true if the buffer is valid
        """
        return self.data is not None and self.read_pos >= 0 and self.read_pos <= self.end_pos

    @property
    def remain(self) -> int:
        """
        Returns the number of bytes left to read
        """
        return self.end_pos - self.read_pos

    def read_dynamic_value(self, size_type: apx_base.SizeType) -> tuple[apx_base.Result, int | None]:
        """
        Reads an integer from the buffer. The size of the integer is set by size_type argument.
        """
        if size_type == apx_base.SizeType.UNSUPPORTED:
            return apx_base.Result.INVALID_ARGUMENT_ERROR, None
        length_size = apx_base.SIZE_TYPE_SIZE[size_type.value]
        if (self.read_pos + length_size) > self.end_pos:
            return apx_base.Result.BUFFER_BOUNDARY_ERROR, None
        value = struct.unpack_from(DYNAMIC_SIZE_STRUCT[size_type.value], self.data, self.read_pos)
        self.read_pos += length_size
        return apx_base.Result.NO_ERROR, value[0]

    def update_padded_read(self, value: int):
        """
        Sets the padded read position relative to current
        read position.
        """
        self.padded_read_pos = self.read_pos + value

    def read_bytes(self, size: int) -> tuple[apx_base.Result, bytearray | None]:
        if size > self.remain:
            return apx_base.Result.BUFFER_BOUNDARY_ERROR, None
        data = bytearray(self.data[self.read_pos:self.read_pos + size])
        self.read_pos += size
        return apx_base.Result.NO_ERROR, data


class DeserializerState:
    """
    APX data deserializer state
    """
    def __init__(self, buffer: ReadBuffer | None = None, parent: "DeserializerState | None" = None) -> None:
        self.buffer = buffer
        self.parent = parent
        self.endianness = "<"
        self.value: Any = None
        self.type_code: apx_base.TypeCode | None = None
        self.dynamic_size_type: apx_base.SizeType | None = None
        self.element_size: int = 0
        self.length_size: int = 0
        self.array_len: int = 0
        self.max_array_len: int = 0
        self.field_name: str | None = None
        self.array_index: int = 0
        self.range_checkers = {apx_base.TypeCode.UINT8: self._check_uint8_range,
                               apx_base.TypeCode.UINT16: self._check_uint16_range,
                               apx_base.TypeCode.UINT32: self._check_uint32_range,
                               apx_base.TypeCode.UINT64: self._check_uint64_range,
                               apx_base.TypeCode.INT8: self._check_int8_range,
                               apx_base.TypeCode.INT16: self._check_int16_range,
                               apx_base.TypeCode.INT32: self._check_int32_range,
                               apx_base.TypeCode.INT64: self._check_int64_range}

        self.format_character = [
            '',    # NONE
            'B',   # UINT8
            'H',   # UINT16
            'L',   # UINT32
            'Q',   # UINT64
            'b',   # INT8
            'h',   # INT16
            'l',   # INT32
            'q',   # INT64
            'c',   # CHAR
            'c',   # CHAR8
            '2s',  # CHAR16
            '4s',  # CHAR32
            '?',   # BOOL
        ]

    @property
    def is_scalar_type_code(self) -> bool:
        type_code = self.type_code.value
        if type_code >= apx_base.TypeCode.UINT8.value and type_code <= apx_base.TypeCode.INT64.value:
            return True
        return self.type_code == apx_base.TypeCode.BOOL

    @property
    def is_string_type_code(self) -> bool:
        type_code = self.type_code.value
        if type_code >= apx_base.TypeCode.CHAR.value and type_code <= apx_base.TypeCode.CHAR32.value:
            return True
        return False

    @property
    def is_byte_type_code(self) -> bool:
        return self.type_code == apx_base.TypeCode.BYTE

    def prepare_for_buffer_read(self) -> apx_base.Result:
        """
        Perform actions that depends on outcome of previous read instructions
        """
        if (self.buffer is None) or (not self.buffer.is_valid):
            return apx_base.Result.MISSING_BUFFER_ERROR
        if self.buffer.padded_read_pos is not None:
            if (self.buffer.padded_read_pos < 0) or (self.buffer.padded_read_pos > self.buffer.end_pos):
                return apx_base.Result.BUFFER_BOUNDARY_ERROR
            self.buffer.read_pos = self.buffer.padded_read_pos
            self.buffer.padded_read_pos = None
        self.clear()
        return apx_base.Result.NO_ERROR

    def clear(self) -> None:
        """
        Clear state
        """
        self.type_code = None
        self.dynamic_size_type = None
        self.element_size = 0
        self.length_size = 0
        self.array_len = 0
        self.max_array_len = 0
        self.array_index = 0

    def check_value_in_range(self, lower_limit: int, upper_limit: int) -> apx_base.Result:
        """
        Checks if current value is in within the upper and lower limit
        Formula: lower_limit <= self.value <= upper_limit
        """
        if self.array_len == 0:
            result = self._check_value_in_range_internal(self.value, lower_limit, upper_limit)
            if result != apx_base.Result.NO_ERROR:
                return result
        else:
            if self.is_scalar_type_code:
                if not isinstance(self.value, list):
                    return apx_base.Result.VALUE_TYPE_ERROR
                for child in self.value:
                    result = self._check_value_in_range_internal(child, lower_limit, upper_limit)
                    if result != apx_base.Result.NO_ERROR:
                        return result
            else:
                return apx_base.Result.UNSUPPORTED_ERROR
        return apx_base.Result.NO_ERROR

    def read_value(self) -> apx_base.Result:
        if self.dynamic_size_type is not None:
            result = self.read_dynamic_value_from_buffer(self.array_len, self.dynamic_size_type)
            if result != apx_base.Result.NO_ERROR:
                return result
        if self.is_byte_type_code:
            return self.read_byte_array()
        elif self.array_len == 0:
            return self.read_scalar_value()
        else:
            if self.is_scalar_type_code:
                return self.read_array_of_scalar_values()
            elif self.is_string_type_code:
                return self.read_string_value()
        return apx_base.Result.NOT_IMPLEMENTED_ERROR

    def read_string_value(self) -> apx_base.Result:
        assert self.array_len > 0
        result, value = self.buffer.read_bytes(self.array_len)
        if result != apx_base.Result.NO_ERROR:
            return result
        self.value = self.strip_trailing_zeros(value)
        if self.type_code == apx_base.TypeCode.CHAR8:
            encoding = "UTF-8"
        elif self.type_code == apx_base.TypeCode.CHAR16:
            encoding = "UTF-16"
        elif self.type_code == apx_base.TypeCode.CHAR32:
            encoding = "UTF-32"
        else:
            encoding = "ASCII"
        self.value = str(self.value, encoding=encoding)
        return apx_base.Result.NO_ERROR

    def read_byte_array(self) -> apx_base.Result:
        """
        Read bytes from buffer
        """
        num_bytes = 1 if self.array_len == 0 else self.array_len
        result, value = self.buffer.read_bytes(num_bytes)
        if result != apx_base.Result.NO_ERROR:
            return result
        self.value = bytes(value)
        return apx_base.Result.NO_ERROR

    def read_dynamic_value_from_buffer(self, value: int, size_type: apx_base.SizeType) -> apx_base.Result:
        return apx_base.Result.NOT_IMPLEMENTED_ERROR

    def read_scalar_value(self) -> apx_base.Result:
        if self.type_code == apx_base.TypeCode.UINT8:
            self._unpack_uint8_value()
        else:
            self._unpack_scalar_value()
        self.buffer.read_pos += self.element_size
        return apx_base.Result.NO_ERROR

    def read_array_of_scalar_values(self) -> apx_base.Result:
        pack_code = self.format_character[self.type_code.value]
        assert pack_code
        fmt_str = f"{self.endianness}{self.array_len}{pack_code}"
        if self.buffer.remain < (self.array_len * self.element_size):
            return apx_base.Result.BUFFER_BOUNDARY_ERROR
        try:
            self.value = list(struct.unpack_from(fmt_str, self.buffer.data, self.buffer.read_pos))
        except struct.error:
            return apx_base.Result.UNPACK_ERROR
        self.buffer.read_pos += self.element_size * self.array_len
        return apx_base.Result.NO_ERROR

    def strip_trailing_zeros(self, data: bytearray) -> bytearray:
        """
        Returns the incoming bytearray with any trailing
        zeros stripped away
        """
        count = 0
        index = len(data) - 1
        while index >= 0:
            if data[index] != 0:
                break
            count += 1
            index -= 1
        if count > 0:
            return data[0:len(data) - count]
        return data

    def init_array(self) -> None:
        """
        Sets the state value to an array
        """
        self.value = []

    def init_record(self) -> None:
        """
        Sets the state value to a dictionary
        """
        self.value = {}

    def set_field_name(self, field_name: str) -> None:
        """
        Selects the next field name of the record
        """
        self.field_name = field_name

    def create_field_in_record(self, value: Any) -> apx_base.Result:
        """
        Creates a new elment in the internal dict
        """
        assert isinstance(self.value, dict)
        if not self.field_name:
            return apx_base.Result.NAME_MISSING_ERROR
        self.value[self.field_name] = value
        return apx_base.Result.NO_ERROR

    def append_value_to_array(self, value: Any) -> apx_base.Result:
        """
        Appends value to internal array
        """
        assert isinstance(self.value, list)
        self.value.append(value)
        return apx_base.Result.NO_ERROR

    def _check_value_in_range_internal(self, value: int, lower_limit: int, upper_limit: int) -> apx_base.Result:
        if isinstance(value, int):
            if value < lower_limit or value > upper_limit:
                return apx_base.Result.VALUE_RANGE_ERROR
        else:
            return apx_base.Result.VALUE_TYPE_ERROR
        return apx_base.Result.NO_ERROR

    def _check_uint8_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT8_MAX)

    def _check_uint16_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT16_MAX)

    def _check_uint32_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT32_MAX)

    def _check_uint64_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT64_MAX)

    def _check_int8_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT8_MIN, apx_base.INT8_MAX)

    def _check_int16_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT16_MIN, apx_base.INT16_MAX)

    def _check_int32_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT32_MIN, apx_base.INT32_MAX)

    def _check_int64_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT64_MIN, apx_base.INT64_MAX)

    def _unpack_uint8_value(self) -> None:
        self.value = self.buffer.data[self.buffer.read_pos]

    def _unpack_scalar_value(self) -> None:
        pack_code = self.format_character[self.type_code.value]
        assert pack_code
        fmt_str = f"{self.endianness}{pack_code}"
        try:
            self.value = struct.unpack_from(fmt_str, self.buffer.data, self.buffer.read_pos)[0]
        except struct.error:
            return apx_base.Result.UNPACK_ERROR
        if self.is_string_type_code:
            if self.type_code == apx_base.TypeCode.CHAR8:
                encoding = "UTF-8"
            elif self.type_code == apx_base.TypeCode.CHAR16:
                encoding = "UTF-16"
            elif self.type_code == apx_base.TypeCode.CHAR32:
                encoding = "UTF-32"
            else:
                encoding = "ASCII"
            self.value = str(self.value, encoding=encoding)
        return apx_base.Result.NO_ERROR


class Deserializer:
    """
    APX data deserializer
    """

    def __init__(self) -> None:
        self.read_buffer: ReadBuffer | None = None
        self.state = DeserializerState()
        self.stack: deque[DeserializerState] = deque()

    @property
    def has_valid_buffer(self) -> bool:
        return self.read_buffer is not None and self.read_buffer.is_valid

    def set_read_buffer(self, buffer: bytes | bytearray) -> None:
        """
        Selects the buffer to read from
        """
        self.read_buffer = ReadBuffer(buffer)
        self.state.buffer = self.read_buffer

    def bytes_read(self) -> int:
        if (self.state.buffer is None) or (not self.state.buffer.is_valid):
            return -1
        return self.state.buffer.read_pos

    def value(self) -> Any:
        return self.state.value

    def check_value_range(self, lower_limit: int, upper_limit: int) -> apx_base.Result:
        """
        Checks if unpacked value is in range
        """
        return self.state.check_value_in_range(lower_limit, upper_limit)

    def unpack_uint8(self,
                     array_len: int = 0,
                     dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint8
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.UINT8
        self.state.element_size = apx_base.UINT8_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_uint16(self,
                      array_len: int = 0,
                      dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint16
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.UINT16
        self.state.element_size = apx_base.UINT16_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_uint32(self,
                      array_len: int = 0,
                      dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint32
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.UINT32
        self.state.element_size = apx_base.UINT32_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_uint64(self,
                      array_len: int = 0,
                      dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint64
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.UINT64
        self.state.element_size = apx_base.UINT64_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_int8(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint8
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.INT8
        self.state.element_size = apx_base.INT8_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_int16(self,
                     array_len: int = 0,
                     dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint16
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.INT16
        self.state.element_size = apx_base.INT16_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_int32(self,
                     array_len: int = 0,
                     dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint32
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.INT32
        self.state.element_size = apx_base.INT32_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_int64(self,
                     array_len: int = 0,
                     dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type uint64
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.INT64
        self.state.element_size = apx_base.INT64_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_char(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type char
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.CHAR
        self.state.element_size = apx_base.CHAR_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_char8(self,
                     array_len: int = 0,
                     dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type char8 (UTF-8)
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.CHAR8
        self.state.element_size = apx_base.CHAR8_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_bool(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type boolean
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.BOOL
        self.state.element_size = apx_base.BOOL_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_byte(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Unpack value(s) of type byte
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.BYTE
        self.state.element_size = apx_base.BYTE_SIZE
        return self._unpack_value(array_len, dynamic_size_type)

    def unpack_record(self,
                      array_len: int = 0,
                      dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Prepares to read a new record
        """
        result = self.state.prepare_for_buffer_read()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.clear()
        self.state.type_code = apx_base.TypeCode.RECORD
        if array_len > 0:
            result = self._prepare_for_array(array_len, dynamic_size_type)
            if result != apx_base.Result.NO_ERROR:
                return result
            self.state.init_array()
            self._enter_record_child_state()
        else:
            self.state.init_record()
        return result

    def record_select(self, field_name: str, is_first_field: bool) -> apx_base.Result:
        """
        Sets next record field name
        """
        if not is_first_field:
            result = self._pop_state()
            if result != apx_base.Result.NO_ERROR:
                return result
        if self.state.type_code != apx_base.TypeCode.RECORD or not isinstance(self.state.value, dict):
            return apx_base.Result.VALUE_TYPE_ERROR
        self.state.set_field_name(field_name)
        self._enter_empty_child_state()
        return apx_base.Result.NO_ERROR

    def record_end(self) -> apx_base.Result:
        """
        Ends current record
        """
        return self._pop_state()

    def array_next(self) -> tuple[apx_base.Result, bool]:
        """
        Advances to next element in array of records
        """
        result = self._pop_state()
        if result != apx_base.Result.NO_ERROR:
            return result, False
        if not isinstance(self.state.value, list):
            return apx_base.Result.VALUE_TYPE_ERROR, False
        if self.state.array_len > 0:
            self.state.array_index += 1
            if self.state.array_index == self.state.array_len:
                return apx_base.Result.NO_ERROR, True
            else:
                if self.state.type_code == apx_base.TypeCode.RECORD:
                    self._enter_record_child_state()
                    return apx_base.Result.NO_ERROR, False
                else:
                    return apx_base.Result.NOT_IMPLEMENTED_ERROR, False
        return apx_base.Result.INTERNAL_ERROR, False

    def _enter_record_child_state(self) -> None:
        """
        Creates and enters new child state and initializes it to
        be of type record
        """
        child_state = DeserializerState(self.read_buffer, self.state)
        child_state.type_code = apx_base.TypeCode.RECORD
        child_state.init_record()
        self.stack.append(self.state)
        self.state = child_state

    def _enter_empty_child_state(self) -> None:
        """
        Creates and enters new empty child state
        """
        child_state = DeserializerState(self.read_buffer, self.state)
        self.stack.append(self.state)
        self.state = child_state

    def _unpack_value(self, array_len: int, dynamic_size_type: apx_base.SizeType | None) -> apx_base.Result:
        """
        Unpacks value from read buffer
        """
        if array_len > 0:
            result = self._prepare_for_array(array_len, dynamic_size_type)
            if result != apx_base.Result.NO_ERROR:
                return result
        return self.state.read_value()

    def _prepare_for_array(self, array_len: int, dynamic_size_type: apx_base.SizeType | None) -> apx_base.Result:
        """
        Prepares for reading array data
        """
        if array_len > 0:
            if dynamic_size_type is not None:
                self.state.max_array_len = array_len
                result, value = self.read_buffer.read_dynamic_value(dynamic_size_type)
                if result != apx_base.Result.NO_ERROR:
                    return result
                if value > self.state.max_array_len:
                    return apx_base.Result.VALUE_LENGTH_ERROR
                self.state.array_len = value
                assert self.state.element_size > 0
                self.read_buffer.update_padded_read(self.state.max_array_len * self.state.element_size)
            else:
                self.state.array_len = array_len
        return apx_base.Result.NO_ERROR

    def _pop_state(self) -> apx_base.Result:
        """
        Pops current state from the state stack
        """
        if len(self.stack) > 0:
            child_state = self.state
            self.state = self.stack.pop()
            if self.state.type_code == apx_base.TypeCode.RECORD:
                if isinstance(self.state.value, dict):
                    return self.state.create_field_in_record(child_state.value)
                elif isinstance(self.state.value, list):
                    return self.state.append_value_to_array(child_state.value)
                else:
                    return apx_base.Result.NOT_IMPLEMENTED_ERROR
            else:
                return apx_base.Result.NOT_IMPLEMENTED_ERROR
        return apx_base.Result.NO_ERROR
