"""
APX byte code compiler for pack and unpack programs
"""
from __future__ import annotations
import apx.base as apx_base
import apx.vm.base as apx_vm_base
import apx.vm.program
import apx.model as apx_model


class Compiler:
    """
    Compiles port and data element definitions into APX VM bytecode programs.
    """

    def __init__(self) -> None:
        self.is_pack_prog: bool = False
        self.program: apx.vm.program.Encoder = apx.vm.program.Encoder()
        self.is_dynamic: bool = False

    def compile_port(self, port: apx_model.Port,
                     program_type: apx_vm_base.ProgramType) -> tuple[apx_base.Result, bytes | None]:
        """
        Compiles a port into an APX bytecode program.
        """
        data_element = port.effective_element
        if data_element is None:
            return apx_base.NULL_PTR_ERROR, None
        rc, data_size = self.compile_data_element(program_type, data_element)
        if rc != apx_base.NO_ERROR:
            return rc, None
        queue_len = port.queue_len
        rc = self.program.encode_program_header(program_type, data_size, queue_len, self.is_dynamic)
        if rc != apx_base.NO_ERROR:
            return rc, None
        return apx_base.NO_ERROR, bytes(self.program.header) + bytes(self.program.buffer)

    def compile_data_element(self, program_type: apx_vm_base.ProgramType,
                             data_element: apx_model.DataElement) -> tuple[apx_base.Result, int]:
        """
        Compiles a data element into bytecode instructions.
        """
        elem_size: int | None = None
        is_array = data_element.is_array
        type_code = data_element.type_code

        if type_code == apx_base.TypeCode.RECORD:
            rc, elem_size = self.compile_pack_unpack_record_data_element(program_type, data_element)
        else:
            rc, elem_size = self.compile_pack_unpack_simple_data_element(program_type, data_element)
        if rc != apx_base.NO_ERROR:
            return rc, 0
        assert elem_size is not None
        if is_array:
            is_dynamic_array = data_element.is_dynamic_array
            array_len = data_element.array_len
            assert array_len is not None
            data_size = elem_size * array_len
            if is_dynamic_array:
                data_size += apx.vm.program.calc_size_type_to_size(apx.vm.program.calc_value_to_size_type(array_len))
        else:
            data_size = elem_size
        return apx_base.NO_ERROR, data_size

    def compile_pack_unpack_record_data_element(
            self, program_type: apx_vm_base.ProgramType,
            data_element: apx_model.DataElement) -> tuple[apx_base.Result, int | None]:
        """
        Compiles pack/unpack instructions for a record data element.
        """
        retval = apx_base.NO_ERROR
        elem_size: int | None = None
        is_array = data_element.is_array
        if program_type == apx_vm_base.ProgramType.PACK:
            opcode = apx_vm_base.OpCode.PACK
        else:
            opcode = apx_vm_base.OpCode.UNPACK
        self.program.encode_instruction(opcode, apx_vm_base.Variant.RECORD, is_array)
        if is_array:
            is_dynamic_array = data_element.is_dynamic_array
            array_len = data_element.array_len
            assert array_len is not None
            rc = self.compile_array_size_instruction(array_len, is_dynamic_array)
            if rc != apx_base.NO_ERROR:
                return rc, 0
            if is_dynamic_array:
                self.is_dynamic = True
        retval, elem_size = self.compile_record_fields(program_type, data_element)
        if retval == apx_base.NO_ERROR and is_array:
            self.compile_array_next_instruction()
        return retval, elem_size

    def compile_record_fields(self, program_type: apx_vm_base.ProgramType,
                              data_element: apx_model.DataElement) -> tuple[apx_base.Result, int]:
        """
        Compiles child elements of a record structure.
        """
        record_size = 0
        assert data_element.type_code == apx_base.TypeCode.RECORD
        assert data_element.elements is not None
        for i, child_element in enumerate(data_element.elements):
            rc = self.compile_record_select_instruction(child_element, is_first_field=i == 0)
            if rc != apx_base.NO_ERROR:
                return rc, 0
            rc, child_elem_size = self.compile_data_element(program_type, child_element)
            if rc != apx_base.NO_ERROR:
                return rc, 0
            if child_elem_size == 0:
                return apx_base.LENGTH_ERROR, 0
            record_size += child_elem_size
        rc = self.compile_record_end_instruction()
        if rc != apx_base.NO_ERROR:
            return rc, 0
        return apx_base.NO_ERROR, record_size

    def compile_record_select_instruction(
        self, data_element: apx_model.DataElement, is_first_field: bool
    ) -> apx_base.Result:
        """
        Compiles a RECORD_SELECT instruction for selecting a named field.
        """
        name = data_element.name
        if name is None or len(name) == 0:
            return apx_base.NAME_MISSING_ERROR
        self.program.encode_instruction(apx_vm_base.OpCode.DATA_CTRL, apx_vm_base.Variant.RECORD_SELECT, is_first_field)
        return self.program.encode_field_name(name)

    def compile_record_end_instruction(self) -> apx_base.Result:
        """
        Compiles a RECORD_END instruction.
        """
        return self.program.encode_instruction(
            apx_vm_base.OpCode.DATA_CTRL, apx_vm_base.Variant.RECORD_END, False)

    def compile_array_next_instruction(self) -> apx_base.Result:
        """
        Compiles an ARRAY_NEXT flow control instruction.
        """
        return self.program.encode_instruction(
            apx_vm_base.OpCode.FLOW_CTRL, apx_vm_base.Variant.ARRAY_NEXT, False)

    def compile_pack_unpack_simple_data_element(
        self,
        program_type: apx_vm_base.ProgramType,
        data_element: apx_model.DataElement
    ) -> tuple[apx_base.Result, int]:
        """
        Compiles pack/unpack instructions for a primitive data element.
        """
        retval = apx_base.NO_ERROR
        elem_size: int | None = None
        data_variant: apx_vm_base.Variant | None = None
        limit_check_variant: apx_vm_base.Variant | None = None
        is_array = data_element.is_array
        type_code = data_element.type_code
        has_limits = data_element.has_limits
        if program_type == apx_vm_base.ProgramType.PACK:
            opcode = apx_vm_base.OpCode.PACK
            is_pack_prog = True
        else:
            opcode = apx_vm_base.OpCode.UNPACK
            is_pack_prog = False
        if type_code == apx_base.TypeCode.UINT8:
            data_variant = apx_vm_base.Variant.UINT8
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_UINT8
            elem_size = apx_vm_base.UINT8_SIZE
        elif type_code == apx_base.TypeCode.UINT16:
            data_variant = apx_vm_base.Variant.UINT16
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_UINT16
            elem_size = apx_vm_base.UINT16_SIZE
        elif type_code == apx_base.TypeCode.UINT32:
            data_variant = apx_vm_base.Variant.UINT32
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_UINT32
            elem_size = apx_vm_base.UINT32_SIZE
        elif type_code == apx_base.TypeCode.UINT64:
            data_variant = apx_vm_base.Variant.UINT64
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_UINT64
            elem_size = apx_vm_base.UINT64_SIZE
        elif type_code == apx_base.TypeCode.INT8:
            data_variant = apx_vm_base.Variant.INT8
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_INT8
            elem_size = apx_vm_base.INT8_SIZE
        elif type_code == apx_base.TypeCode.INT16:
            data_variant = apx_vm_base.Variant.INT16
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_INT16
            elem_size = apx_vm_base.INT16_SIZE
        elif type_code == apx_base.TypeCode.INT32:
            data_variant = apx_vm_base.Variant.INT32
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_INT32
            elem_size = apx_vm_base.INT32_SIZE
        elif type_code == apx_base.TypeCode.INT64:
            data_variant = apx_vm_base.Variant.INT64
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_INT64
            elem_size = apx_vm_base.INT64_SIZE
        elif type_code == apx_base.TypeCode.BOOL:
            data_variant = apx_vm_base.Variant.BOOL
            limit_check_variant = None
            elem_size = apx_vm_base.UINT8_SIZE
        elif type_code == apx_base.TypeCode.BYTE:
            data_variant = apx_vm_base.Variant.BYTE
            limit_check_variant = apx_vm_base.Variant.LIMIT_CHECK_UINT8
            elem_size = apx_vm_base.UINT8_SIZE
        elif type_code == apx_base.TypeCode.CHAR:
            data_variant = apx_vm_base.Variant.CHAR
            elem_size = apx_vm_base.INT8_SIZE
        elif type_code == apx_base.TypeCode.CHAR8:
            data_variant = apx_vm_base.Variant.CHAR8
            elem_size = apx_vm_base.UINT8_SIZE
        elif type_code == apx_base.TypeCode.CHAR16:
            data_variant = apx_vm_base.Variant.CHAR16
            elem_size = apx_vm_base.UINT16_SIZE
        elif type_code == apx_base.TypeCode.CHAR32:
            data_variant = apx_vm_base.Variant.CHAR32
            elem_size = apx_vm_base.UINT32_SIZE
        else:
            return apx_base.ELEMENT_TYPE_ERROR, 0
        if has_limits and is_pack_prog:
            if limit_check_variant is None:
                return apx_base.INVALID_INSTRUCTION_ERROR, 0
            rc = self.compile_limit_check_instruction(data_element, limit_check_variant, is_array)
            if rc != apx_base.NO_ERROR:
                return rc, 0
        assert data_variant is not None
        self.compile_data_instruction(opcode, data_variant, is_array)
        if is_array:
            is_dynamic_array = data_element.is_dynamic_array
            array_len = data_element.array_len
            assert array_len is not None
            rc = self.compile_array_size_instruction(array_len, is_dynamic_array)
            if rc != apx_base.NO_ERROR:
                return rc, 0
        if has_limits and not is_pack_prog:
            if limit_check_variant is None:
                return apx_base.INVALID_INSTRUCTION_ERROR, 0
            rc = self.compile_limit_check_instruction(data_element, limit_check_variant, is_array)
            if rc != apx_base.NO_ERROR:
                return rc, 0
        return retval, elem_size

    def compile_data_instruction(self, opcode: apx_vm_base.OpCode,
                                 data_variant: apx_vm_base.Variant, is_array: bool) -> None:
        """
        Encodes a pack/unpack data instruction into the program buffer.
        """
        self.program.encode_instruction(opcode, data_variant, is_array)

    def compile_array_size_instruction(self, array_len: int, is_dynamic_array: bool) -> apx_base.Result:
        """
        Encodes an array size instruction into the program buffer.
        """
        retval = self.program.encode_array_size(array_len, is_dynamic_array)
        if retval == apx_base.NO_ERROR and is_dynamic_array:
            self.is_dynamic = True
        return retval

    def compile_limit_check_instruction(self, data_element: apx_model.DataElement,
                                        limit_check_variant: apx_vm_base.Variant,
                                        is_array: bool) -> apx_base.Result:
        """
        Encodes a limit check instruction into the program buffer.
        """
        lower_limit, upper_limit = data_element.get_limits()
        assert lower_limit is not None and upper_limit is not None
        return self.program.encode_limit_check_instruction(
            limit_check_variant, lower_limit, upper_limit, is_array
        )
