"""
APX data serializer
"""
import struct
from typing import Any, Union
import apx.base as apx_base


SCALAR_TYPES = {apx_base.TypeCode.UINT8,
                apx_base.TypeCode.UINT16,
                apx_base.TypeCode.UINT32,
                apx_base.TypeCode.UINT64,
                apx_base.TypeCode.INT8,
                apx_base.TypeCode.INT16,
                apx_base.TypeCode.INT32,
                apx_base.TypeCode.INT64,
                apx_base.TypeCode.BOOL,
                apx_base.TypeCode.BYTE,
                }

SIZE_TYPE_FORMAT = ["B", "H", "L", None]
SIZE_TYPE_MAX = [apx_base.UINT8_MAX,
                 apx_base.UINT16_MAX,
                 apx_base.UINT32_MAX,
                 None]


class WriteBuffer:
    """
    Write buffer wrapper
    """
    def __init__(self, data: bytearray) -> None:
        self.data = data
        self.write_pos = 0
        self.end_pos = len(data)
        self.padded_write_pos: int | None = None

    @property
    def is_valid(self) -> bool:
        """
        Returns true if the buffer is valid
        """
        return self.data is not None and self.write_pos >= 0 and self.write_pos <= self.end_pos

    @property
    def remain(self) -> int:
        """
        Returns the number of bytes remaining in buffer
        """
        return self.end_pos - self.write_pos

    def write_bytes(self, data: bytes | bytearray) -> apx_base.Result:
        """
        Writes data bytes into the buffer.
        """
        size = len(data)
        if size > self.remain:
            return apx_base.Result.BUFFER_BOUNDARY_ERROR
        self.data[self.write_pos:self.write_pos + size] = data
        self.write_pos += size
        return apx_base.Result.NO_ERROR


class SerializerState:
    """
    APX data serializer state
    """
    def __init__(self, buffer: WriteBuffer | None = None, parent: Union["SerializerState", None] = None) -> None:
        self.parent = parent
        self.type_code: apx_base.TypeCode | None = None
        self.dynamic_size_type: apx_base.SizeType | None = None
        self.element_size: int = 0
        # self.length_size: int = 0
        self.buffer = buffer
        self.value: Any = None
        self.array_len: int = 0
        self.endianness: str = "<"
        self.max_array_len: int = 0
        self.field_name: str | None = None
        self.array_index: int = 0
        self.range_checkers = {apx_base.TypeCode.UINT8: self._check_uint8_range,
                               apx_base.TypeCode.UINT16: self._check_uint16_range,
                               apx_base.TypeCode.UINT32: self._check_uint32_range,
                               apx_base.TypeCode.INT8: self._check_int8_range,
                               apx_base.TypeCode.INT16: self._check_int16_range,
                               apx_base.TypeCode.INT32: self._check_int32_range}
        self.write_handlers = {apx_base.TypeCode.UINT8: self._pack_uint8_value,
                               apx_base.TypeCode.UINT16: self._pack_scalar_value,
                               apx_base.TypeCode.UINT32: self._pack_scalar_value,
                               apx_base.TypeCode.UINT64: self._pack_scalar_value,
                               apx_base.TypeCode.INT8: self._pack_scalar_value,
                               apx_base.TypeCode.INT16: self._pack_scalar_value,
                               apx_base.TypeCode.INT32: self._pack_scalar_value,
                               apx_base.TypeCode.INT64: self._pack_scalar_value,
                               apx_base.TypeCode.BOOL: self._pack_bool_value}

        self.format_character = [
            '',   # NONE
            'B',  # UINT8
            'H',  # UINT16
            'L',  # UINT32
            'Q',  # UINT64
            'b',  # INT8
            'h',  # INT16
            'l',  # INT32
            'q',  # INT64
            'c',  # CHAR
            '',   # CHAR8
            '',   # CHAR16
            '',   # CHAR32
            '?',  # BOOL
            '',   # BYTE
            '',   # RECORD
        ]

    @property
    def is_scalar_type_code(self) -> bool:
        """
        Returns True if type_code is a scalar type.
        """
        type_code = self.type_code.value
        if apx_base.TypeCode.UINT8.value <= type_code <= apx_base.TypeCode.INT64.value:
            return True
        return self.type_code == apx_base.TypeCode.BOOL

    @property
    def is_string_type_code(self) -> bool:
        """
        Returns True if type_code is a string type.
        """
        type_code = self.type_code.value
        return apx_base.TypeCode.CHAR.value <= type_code <= apx_base.TypeCode.CHAR32.value

    @property
    def is_byte_type_code(self) -> bool:
        """
        Returns True if type_code is BYTE.
        """
        return self.type_code == apx_base.TypeCode.BYTE

    @property
    def is_record_type_code(self) -> bool:
        """
        Returns True if type_code is RECORD.
        """
        return self.type_code == apx_base.TypeCode.RECORD

    @property
    def is_scalar_value(self) -> bool:
        """
        Returns True if value is a scalar.
        """
        return isinstance(self.value, (int, str, bytes, bool))

    @property
    def is_str_value(self) -> bool:
        """
        Returns True if value is a string.
        """
        return isinstance(self.value, str)

    @property
    def is_byte_like_value(self) -> bool:
        """
        Returns True if value is bytes or bytearray.
        """
        return isinstance(self.value, (bytes, bytearray))

    def prepare_for_array(self,
                          array_len: int,
                          dynamic_size_type: apx_base.SizeType | None = None) -> apx_base.Result:
        """
        Prepare for writing array
        Does multiple checks if array data will fit etc.
        """
        if dynamic_size_type is None:
            self.array_len = array_len
        else:
            self.max_array_len = array_len
            self.array_len = len(self.value)
            self.dynamic_size_type = dynamic_size_type
            length_size = apx_base.SIZE_TYPE_SIZE[dynamic_size_type.value]
            assert length_size is not None
            if self.array_len > self.max_array_len:
                return apx_base.Result.VALUE_LENGTH_ERROR
            self.buffer.padded_write_pos = self.buffer.write_pos + length_size + (
                self.max_array_len * self.element_size)
            if self.buffer.padded_write_pos > self.buffer.end_pos:
                return apx_base.Result.BUFFER_BOUNDARY_ERROR
        return apx_base.Result.NO_ERROR

    def prepare_for_buffer_write(self) -> apx_base.Result:
        """
        Performs actions that depend on outcome of previous write instructions
        """
        if (self.buffer is None) or (not self.buffer.is_valid):
            return apx_base.Result.MISSING_BUFFER_ERROR
        if self.buffer.padded_write_pos is not None:
            if (self.buffer.padded_write_pos < 0) or (self.buffer.padded_write_pos > self.buffer.end_pos):
                return apx_base.Result.BUFFER_BOUNDARY_ERROR
            self.buffer.write_pos = self.buffer.padded_write_pos
            self.buffer.padded_write_pos = None
        return apx_base.Result.NO_ERROR

    def check_value_in_range(self, lower_limit: int, upper_limit: int) -> apx_base.Result:
        """
        Checks if current value is in within the upper and lower limit
        Formula: lower_limit <= self.value <= upper_limit
        """
        if isinstance(self.value, int):
            if self.value < lower_limit or self.value > upper_limit:
                return apx_base.Result.VALUE_RANGE_ERROR
        else:
            return apx_base.Result.VALUE_TYPE_ERROR
        return apx_base.Result.NO_ERROR

    def write_value(self) -> apx_base.Result:
        """
        Writes current state value to the buffer.
        """
        if self.dynamic_size_type is not None:
            result = self._write_dynamic_value_to_buffer(self.array_len, self.dynamic_size_type)
            if result != apx_base.Result.NO_ERROR:
                return result

        if self.is_scalar_type_code:
            if self.dynamic_size_type is None and self.array_len == 0:
                return self.write_scalar_value()
            return self.write_array_of_scalar_values()
        elif self.is_string_type_code:
            return self._write_string()
        elif self.is_byte_type_code:
            return self._write_byte()
        return apx_base.Result.NOT_IMPLEMENTED_ERROR

    def write_scalar_value(self) -> apx_base.Result:
        """
        Writes scalar value to the buffer.
        """
        range_checker = self.range_checkers.get(self.type_code, None)
        if range_checker is not None:
            result = range_checker()
            if result != apx_base.Result.NO_ERROR:
                return result
        handler = self.write_handlers.get(self.type_code, None)
        if handler is not None:
            result = handler()
            if result is not None and result != apx_base.Result.NO_ERROR:
                return result
            self.buffer.write_pos += self.element_size
        else:
            return apx_base.Result.NOT_IMPLEMENTED_ERROR
        return apx_base.Result.NO_ERROR

    def record_select(self, key: str) -> tuple[apx_base.Result, Any]:
        """
        Selects record field from value
        """
        if not isinstance(self.value, dict):
            return apx_base.Result.VALUE_TYPE_ERROR, None
        value = self.value.get(key, None)
        if value is None:
            return apx_base.Result.NOT_FOUND_ERROR, None
        self.field_name = key
        return apx_base.Result.NO_ERROR, value

    def write_array_of_scalar_values(self) -> apx_base.Result:
        """
        Writes array of scalar values to the buffer.
        """
        if not isinstance(self.value, list):
            return apx_base.Result.VALUE_TYPE_ERROR
        if self.dynamic_size_type is None and len(self.value) != self.array_len:
            return apx_base.Result.VALUE_LENGTH_ERROR
        pack_code = self.format_character[self.type_code.value]
        assert pack_code
        fmt_str = f"{self.endianness}{self.array_len}{pack_code}"
        if self.type_code == apx_base.TypeCode.BOOL:
            values = []
            for x in self.value:
                if isinstance(x, (bool, int)):
                    values.append(bool(x))
                else:
                    return apx_base.Result.VALUE_CONVERSION_ERROR
        else:
            values = self.value
        try:
            struct.pack_into(fmt_str, self.buffer.data, self.buffer.write_pos, *values)
        except (struct.error, TypeError, ValueError):
            return apx_base.Result.VALUE_CONVERSION_ERROR
        self.buffer.write_pos += self.element_size * self.array_len
        return apx_base.Result.NO_ERROR

    def _write_byte(self) -> apx_base.Result:
        if isinstance(self.value, (bytes, bytearray)):
            data = bytes(self.value)
        elif isinstance(self.value, int):
            if self.value < 0 or self.value > 255:
                return apx_base.Result.VALUE_RANGE_ERROR
            data = bytes([self.value])
        elif isinstance(self.value, list):
            for x in self.value:
                if not isinstance(x, int) or x < 0 or x > 255:
                    return apx_base.Result.VALUE_RANGE_ERROR
            data = bytes(self.value)
        else:
            return apx_base.Result.VALUE_TYPE_ERROR

        if self.dynamic_size_type is None and self.array_len > 0:
            if len(data) != self.array_len:
                return apx_base.Result.VALUE_LENGTH_ERROR

        return self.buffer.write_bytes(data)

    def _pack_bool_value(self) -> apx_base.Result:
        if isinstance(self.value, (bool, int)):
            self.buffer.data[self.buffer.write_pos] = 1 if self.value else 0
            return apx_base.Result.NO_ERROR
        return apx_base.Result.VALUE_CONVERSION_ERROR

    def _write_string(self) -> apx_base.Result:

        if not self.is_str_value:
            return apx_base.Result.VALUE_TYPE_ERROR
        if self.type_code == apx_base.TypeCode.CHAR8:
            encoding = "UTF-8"
        elif self.type_code == apx_base.TypeCode.CHAR16:
            encoding = "UTF-16"
        elif self.type_code == apx_base.TypeCode.CHAR32:
            encoding = "UTF-32"
        else:
            encoding = "ASCII"
        data = bytearray(self.value, encoding=encoding)
        array_len = 1 if self.array_len == 0 else self.array_len
        max_size = array_len * self.element_size
        if len(data) > max_size:
            return apx_base.Result.VALUE_LENGTH_ERROR
        if self.dynamic_size_type is None and len(data) < max_size:
            data.extend(b"\x00" * (max_size - len(data)))
        return self.buffer.write_bytes(data)

    def _write_dynamic_value_to_buffer(self, value: int, size_type: apx_base.SizeType) -> apx_base.Result:
        format_text = SIZE_TYPE_FORMAT[size_type.value]
        max_value = SIZE_TYPE_MAX[size_type.value]
        write_size = apx_base.SIZE_TYPE_SIZE[size_type.value]
        assert format_text is not None
        if value > max_value:
            return apx_base.Result.LENGTH_ERROR
        struct.pack_into(format_text, self.buffer.data, self.buffer.write_pos, value)
        self.buffer.write_pos += write_size
        return apx_base.Result.NO_ERROR

    def _check_uint8_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT8_MAX)

    def _check_uint16_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT16_MAX)

    def _check_uint32_range(self) -> apx_base.Result:
        return self.check_value_in_range(0, apx_base.UINT32_MAX)

    def _check_int8_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT8_MIN, apx_base.INT8_MAX)

    def _check_int16_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT16_MIN, apx_base.INT16_MAX)

    def _check_int32_range(self) -> apx_base.Result:
        return self.check_value_in_range(apx_base.INT32_MIN, apx_base.INT32_MAX)

    def _pack_uint8_value(self) -> None:
        self.buffer.data[self.buffer.write_pos] = self.value

    def _pack_scalar_value(self) -> None:
        pack_code = self.format_character[self.type_code.value]
        assert pack_code
        fmt_str = f"{self.endianness}{pack_code}"
        struct.pack_into(fmt_str, self.buffer.data, self.buffer.write_pos, self.value)
        return apx_base.Result.NO_ERROR


class Serializer:
    """
    APX data serializer
    """

    def __init__(self) -> None:
        self.write_buffer: WriteBuffer | None = None
        self.state = SerializerState()
        self.stack: list[SerializerState] = []

    def set_write_buffer(self, buffer: bytearray) -> None:
        """
        Selects the buffer to serialize to
        """
        self.write_buffer = WriteBuffer(buffer)
        self.state.buffer = self.write_buffer

    def prepare_for_buffer_write(self) -> apx_base.Result:
        """
        Prepares buffer for write
        """
        return self.state.prepare_for_buffer_write()

    def bytes_written(self) -> int:
        """
        Returns the number of bytes written to the buffer.
        """
        if (self.state.buffer is None) or (not self.state.buffer.is_valid):
            return -1
        return self.state.buffer.write_pos

    def set_value(self, value: Any) -> None:
        """
        Sets the value to be serialized
        """
        self.state.value = value

    def check_value_in_range(self, lower_limit: int, upper_limit: int) -> apx_base.Result:
        """
        Checks if current value is in within the upper and lower limit
        Formula: lower_limit <= self.value <= upper_limit
        """
        return self.state.check_value_in_range(lower_limit, upper_limit)

    def pack_uint8(self,
                   array_len: int = 0,
                   dynamic_size_type: apx_base.SizeType | None = None
                   ) -> apx_base.Result:
        """
        Packs uint8 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.UINT8
        self.state.element_size = apx_base.UINT8_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_uint16(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None
                    ) -> apx_base.Result:
        """
        Packs uint16 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.UINT16
        self.state.element_size = apx_base.UINT16_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_uint32(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None
                    ) -> apx_base.Result:
        """
        Packs uint32 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.UINT32
        self.state.element_size = apx_base.UINT32_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_uint64(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None
                    ) -> apx_base.Result:
        """
        Packs uint64 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.UINT64
        self.state.element_size = apx_base.UINT64_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_int8(self,
                  array_len: int = 0,
                  dynamic_size_type: apx_base.SizeType | None = None
                  ) -> apx_base.Result:
        """
        Packs int8 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.INT8
        self.state.element_size = apx_base.INT8_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_int16(self,
                   array_len: int = 0,
                   dynamic_size_type: apx_base.SizeType | None = None
                   ) -> apx_base.Result:
        """
        Packs int16 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.INT16
        self.state.element_size = apx_base.INT16_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_int32(self,
                   array_len: int = 0,
                   dynamic_size_type: apx_base.SizeType | None = None
                   ) -> apx_base.Result:
        """
        Packs int32 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.INT32
        self.state.element_size = apx_base.INT32_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_int64(self,
                   array_len: int = 0,
                   dynamic_size_type: apx_base.SizeType | None = None
                   ) -> apx_base.Result:
        """
        Packs int64 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.INT64
        self.state.element_size = apx_base.INT64_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_char(self,
                  array_len: int = 0,
                  dynamic_size_type: apx_base.SizeType | None = None
                  ) -> apx_base.Result:
        """
        Packs char value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.CHAR
        self.state.element_size = apx_base.CHAR_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_char8(self,
                   array_len: int = 0,
                   dynamic_size_type: apx_base.SizeType | None = None
                   ) -> apx_base.Result:
        """
        Packs char8 value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.CHAR8
        self.state.element_size = apx_base.CHAR8_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_bool(self,
                  array_len: int = 0,
                  dynamic_size_type: apx_base.SizeType | None = None
                  ) -> apx_base.Result:
        """
        Packs bool value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.BOOL
        self.state.element_size = apx_base.BOOL_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_byte(self,
                  array_len: int = 0,
                  dynamic_size_type: apx_base.SizeType | None = None
                  ) -> apx_base.Result:
        """
        Packs byte value(s) into buffer.
        """
        self.state.type_code = apx_base.TypeCode.BYTE
        self.state.element_size = apx_base.BYTE_SIZE
        return self._pack_value(array_len, dynamic_size_type)

    def pack_record(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None
                    ) -> apx_base.Result:
        """
        Prepares to pack a record into buffer.
        """
        result = self.state.prepare_for_buffer_write()
        if result != apx_base.Result.NO_ERROR:
            return result
        self.state.type_code = apx_base.TypeCode.RECORD
        self.state.element_size = 0
        if self.state.buffer is None:
            return apx_base.Result.MISSING_BUFFER_ERROR
        if self.state.value is None:
            return apx_base.Result.NO_VALUE_ERROR
        if array_len > 0:
            if not isinstance(self.state.value, list):
                return apx_base.Result.VALUE_TYPE_ERROR
            if dynamic_size_type is None and len(self.state.value) != array_len:
                return apx_base.Result.VALUE_LENGTH_ERROR
            self.state.array_len = array_len
            self.state.array_index = 0
            if len(self.state.value) > 0:
                child_value = self.state.value[0]
                self._enter_child_state()
                self.state.value = child_value
        elif not isinstance(self.state.value, dict):
            return apx_base.Result.VALUE_TYPE_ERROR
        return apx_base.Result.NO_ERROR

    def _pack_value(self,
                    array_len: int = 0,
                    dynamic_size_type: apx_base.SizeType | None = None
                    ) -> apx_base.Result:
        if self.state.buffer is None:
            return apx_base.Result.MISSING_BUFFER_ERROR
        if self.state.value is None:
            return apx_base.Result.NO_VALUE_ERROR
        result = self.state.prepare_for_buffer_write()
        if result != apx_base.Result.NO_ERROR:
            return result
        if array_len > 0:
            result = self.state.prepare_for_array(array_len, dynamic_size_type)
            if result != apx_base.Result.NO_ERROR:
                return result
        return self.state.write_value()

    def record_select(self, name: str, is_first_field: bool = True) -> apx_base.Result:
        """
        Selects a record element from current value
        """
        if not is_first_field:
            self._pop_state()
        result, child_value = self.state.record_select(name)
        if result != apx_base.Result.NO_ERROR:
            return result
        self._enter_child_state()
        self.state.value = child_value  # self.state has now changed to the newly entered child state
        return apx_base.Result.NO_ERROR

    def record_end(self) -> apx_base.Result:
        """
        Ends current record
        """
        self._pop_state()
        return apx_base.Result.NO_ERROR

    def array_next(self) -> tuple[apx_base.Result, bool]:
        """
        Advances to next element in array of records
        """
        self._pop_state()
        if not isinstance(self.state.value, list):
            return apx_base.Result.VALUE_TYPE_ERROR, False
        if self.state.array_len > 0:
            self.state.array_index += 1
            if self.state.array_index == self.state.array_len:
                return apx_base.Result.NO_ERROR, True
            else:
                if self.state.type_code == apx_base.TypeCode.RECORD:
                    child_value = self.state.value[self.state.array_index]
                    self._enter_child_state()
                    self.state.value = child_value
                    return apx_base.Result.NO_ERROR, False
                else:
                    return apx_base.Result.NOT_IMPLEMENTED_ERROR, False
        return apx_base.Result.INTERNAL_ERROR, False

    def _enter_child_state(self) -> None:
        """
        Pushes current state to the stack and creates a new child state
        """
        child_state = SerializerState(buffer=self.write_buffer, parent=self.state)
        self.stack.append(self.state)
        self.state = child_state

    def _pop_state(self) -> None:
        if len(self.stack) > 0:
            self.state = self.stack.pop()
