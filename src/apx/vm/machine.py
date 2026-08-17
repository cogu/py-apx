"""
APX Virtual Machine (APX VM 2.1)
"""
from __future__ import annotations
from typing import Any
import apx.base as apx_base
import apx.vm.base as apx_vm_base
from apx.vm.program import Decoder
from apx.data.serializer import Serializer
from apx.data.deserializer import Deserializer


PACK_DISPATCH = {
    apx_base.TypeCode.UINT8: "pack_uint8",
    apx_base.TypeCode.UINT16: "pack_uint16",
    apx_base.TypeCode.UINT32: "pack_uint32",
    apx_base.TypeCode.UINT64: "pack_uint64",
    apx_base.TypeCode.INT8: "pack_int8",
    apx_base.TypeCode.INT16: "pack_int16",
    apx_base.TypeCode.INT32: "pack_int32",
    apx_base.TypeCode.INT64: "pack_int64",
    apx_base.TypeCode.BOOL: "pack_bool",
    apx_base.TypeCode.BYTE: "pack_byte",
    apx_base.TypeCode.CHAR: "pack_char",
    apx_base.TypeCode.CHAR8: "pack_char8",
    apx_base.TypeCode.CHAR16: "pack_char16",
    apx_base.TypeCode.CHAR32: "pack_char32",
}

UNPACK_DISPATCH = {
    apx_base.TypeCode.UINT8: "unpack_uint8",
    apx_base.TypeCode.UINT16: "unpack_uint16",
    apx_base.TypeCode.UINT32: "unpack_uint32",
    apx_base.TypeCode.UINT64: "unpack_uint64",
    apx_base.TypeCode.INT8: "unpack_int8",
    apx_base.TypeCode.INT16: "unpack_int16",
    apx_base.TypeCode.INT32: "unpack_int32",
    apx_base.TypeCode.INT64: "unpack_int64",
    apx_base.TypeCode.BOOL: "unpack_bool",
    apx_base.TypeCode.BYTE: "unpack_byte",
    apx_base.TypeCode.CHAR: "unpack_char",
    apx_base.TypeCode.CHAR8: "unpack_char8",
    apx_base.TypeCode.CHAR16: "unpack_char16",
    apx_base.TypeCode.CHAR32: "unpack_char32",
}

LIMIT_CHECK_OPS = {
    apx_vm_base.OperationType.LIMIT_CHECK_UINT8,
    apx_vm_base.OperationType.LIMIT_CHECK_UINT16,
    apx_vm_base.OperationType.LIMIT_CHECK_UINT32,
    apx_vm_base.OperationType.LIMIT_CHECK_UINT64,
    apx_vm_base.OperationType.LIMIT_CHECK_INT8,
    apx_vm_base.OperationType.LIMIT_CHECK_INT16,
    apx_vm_base.OperationType.LIMIT_CHECK_INT32,
    apx_vm_base.OperationType.LIMIT_CHECK_INT64,
}


def size_to_size_type(array_length: int) -> apx_base.SizeType:
    """
    Converts maximum array length to SizeType enum.
    """
    if array_length <= apx_vm_base.UINT8_MAX:
        return apx_base.SizeType.UINT8
    if array_length <= apx_vm_base.UINT16_MAX:
        return apx_base.SizeType.UINT16
    return apx_base.SizeType.UINT32


class VirtualMachine:
    """
    APX Virtual Machine that executes compiled APX 2.1 pack/unpack bytecode programs.
    """

    def __init__(self) -> None:
        self.serializer = Serializer()
        self.deserializer = Deserializer()
        self.decoder = Decoder()
        self.program_header: apx_vm_base.ProgramHeader | None = None
        self.program_start_pos: int = 0

    def select_program(self, program: bytes | bytearray | memoryview) -> apx_base.Result:
        """
        Selects and parses a bytecode program for execution.
        """
        rc = self.decoder.select_program(program)
        if rc != apx_base.NO_ERROR:
            return rc
        rc, self.program_header = self.decoder.parse_program_header()
        if rc == apx_base.NO_ERROR:
            self.program_start_pos = self.decoder.read_pos
        return rc

    def set_write_buffer(self, buffer: bytearray | memoryview) -> apx_base.Result:
        """
        Sets the destination buffer for serialized data.
        """
        if buffer is None:
            return apx_base.NULL_PTR_ERROR
        self.serializer.set_write_buffer(buffer)
        return apx_base.NO_ERROR

    def set_read_buffer(self, buffer: bytes | bytearray | memoryview) -> apx_base.Result:
        """
        Sets the source buffer containing serialized data.
        """
        if buffer is None:
            return apx_base.NULL_PTR_ERROR
        self.deserializer.set_read_buffer(buffer)
        return apx_base.NO_ERROR

    def bytes_written(self) -> int:
        """
        Returns number of bytes written during last pack operation.
        """
        return self.serializer.bytes_written()

    def bytes_read(self) -> int:
        """
        Returns number of bytes read during last unpack operation.
        """
        return self.deserializer.bytes_read()

    def value(self) -> Any:
        """
        Returns the deserialized Python data structure.
        """
        return self.deserializer.value()

    def pack_value(self, value: Any) -> apx_base.Result:
        """
        Packs a Python value into the configured write buffer according to the loaded pack program.
        """
        if self.program_header is None or self.program_header.program_type != apx_vm_base.ProgramType.PACK:
            return apx_base.INVALID_PROGRAM_ERROR
        self.decoder.read_pos = self.program_start_pos
        self.decoder.mark_pos = None
        self.decoder.last_type_code = apx_base.TypeCode.NONE
        self.serializer.set_value(value)
        return self._run_pack_program()

    def unpack_value(self) -> apx_base.Result:
        """
        Unpacks a value from the configured read buffer according to the loaded unpack program.
        """
        if self.program_header is None or self.program_header.program_type != apx_vm_base.ProgramType.UNPACK:
            return apx_base.INVALID_PROGRAM_ERROR
        self.decoder.read_pos = self.program_start_pos
        self.decoder.mark_pos = None
        self.decoder.last_type_code = apx_base.TypeCode.NONE
        return self._run_unpack_program()

    def _run_pack_instruction(self) -> apx_base.Result:
        info = self.decoder.pack_unpack_info
        dynamic_size_type = (
            size_to_size_type(info.array_length)
            if info.is_dynamic_array else None
        )
        if info.type_code == apx_base.TypeCode.RECORD:
            rc = self.serializer.pack_record(info.array_length, dynamic_size_type)
            if rc == apx_base.NO_ERROR and info.array_length > 0:
                self.decoder.save_program_position()
            return rc
        method_name = PACK_DISPATCH.get(info.type_code)
        if method_name is None:
            return apx_base.ELEMENT_TYPE_ERROR
        method = getattr(self.serializer, method_name)
        return method(info.array_length, dynamic_size_type)

    def _run_unpack_instruction(self) -> apx_base.Result:
        info = self.decoder.pack_unpack_info
        dynamic_size_type = (
            size_to_size_type(info.array_length)
            if info.is_dynamic_array else None
        )
        if info.type_code == apx_base.TypeCode.RECORD:
            rc = self.deserializer.unpack_record(info.array_length, dynamic_size_type)
            if rc == apx_base.NO_ERROR and info.array_length > 0:
                self.decoder.save_program_position()
            return rc
        method_name = UNPACK_DISPATCH.get(info.type_code)
        if method_name is None:
            return apx_base.ELEMENT_TYPE_ERROR
        method = getattr(self.deserializer, method_name)
        return method(info.array_length, dynamic_size_type)

    def _run_pack_array_next(self) -> apx_base.Result:
        rc, is_last = self.serializer.array_next()
        if rc != apx_base.NO_ERROR:
            return rc
        if not is_last:
            if not self.decoder.has_saved_program_position():
                return apx_base.INVALID_INSTRUCTION_ERROR
            self.decoder.recall_program_position()
        return apx_base.NO_ERROR

    def _run_unpack_array_next(self) -> apx_base.Result:
        rc, is_last = self.deserializer.array_next()
        if rc != apx_base.NO_ERROR:
            return rc
        if not is_last:
            if not self.decoder.has_saved_program_position():
                return apx_base.INVALID_INSTRUCTION_ERROR
            self.decoder.recall_program_position()
        return apx_base.NO_ERROR

    def _run_pack_program(self) -> apx_base.Result:
        while True:
            rc, op_type = self.decoder.parse_next_operation()
            if rc != apx_base.NO_ERROR:
                return rc
            if op_type == apx_vm_base.OperationType.PROGRAM_END:
                break
            if op_type == apx_vm_base.OperationType.PACK:
                rc = self._run_pack_instruction()
            elif op_type in LIMIT_CHECK_OPS:
                rc = self.serializer.check_value_in_range(
                    self.decoder.range_check_info.lower_limit,
                    self.decoder.range_check_info.upper_limit
                )
            elif op_type == apx_vm_base.OperationType.RECORD_SELECT:
                rc = self.serializer.record_select(
                    self.decoder.field_name,
                    self.decoder.is_first_field
                )
            elif op_type == apx_vm_base.OperationType.RECORD_END:
                rc = self.serializer.record_end()
            elif op_type == apx_vm_base.OperationType.ARRAY_NEXT:
                rc = self._run_pack_array_next()
            else:
                return apx_base.INVALID_INSTRUCTION_ERROR
            if rc != apx_base.NO_ERROR:
                return rc
        return apx_base.NO_ERROR

    def _run_unpack_program(self) -> apx_base.Result:
        while True:
            rc, op_type = self.decoder.parse_next_operation()
            if rc != apx_base.NO_ERROR:
                return rc
            if op_type == apx_vm_base.OperationType.PROGRAM_END:
                break
            if op_type == apx_vm_base.OperationType.UNPACK:
                rc = self._run_unpack_instruction()
            elif op_type in LIMIT_CHECK_OPS:
                rc = self.deserializer.check_value_range(
                    self.decoder.range_check_info.lower_limit,
                    self.decoder.range_check_info.upper_limit
                )
            elif op_type == apx_vm_base.OperationType.RECORD_SELECT:
                rc = self.deserializer.record_select(
                    self.decoder.field_name,
                    self.decoder.is_first_field
                )
            elif op_type == apx_vm_base.OperationType.RECORD_END:
                rc = self.deserializer.record_end()
            elif op_type == apx_vm_base.OperationType.ARRAY_NEXT:
                rc = self._run_unpack_array_next()
            else:
                return apx_base.INVALID_INSTRUCTION_ERROR
            if rc != apx_base.NO_ERROR:
                return rc
        return apx_base.NO_ERROR
