# Copyright 2026 by Conny Gustafsson.
# This file is part of the py-apx project and is released under
# the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Any
import apx.base as apx_base

# --- Helper functions


def is_scalar_value(value: Any) -> bool:
    if isinstance(value, (int, str)):
        return True
    return False

# --- Attributes


class PortAttributes:
    """
    Port attributes is a simplification of
    the AUTOSAR COM-SPEC. It stores attributes
    such as:

    - init value
    - parameter attribute
    - queue length

    """
    def __init__(self) -> None:
        self.init_value: Any = None
        self.is_parameter: bool = False
        self.queue_length: int = 0

    @property
    def has_init_value(self) -> bool:
        return self.init_value is not None

    @property
    def is_queued(self) -> bool:
        return self.queue_length > 0


class TypeAttributes:
    """
    Type attributes stores attributes set on
    type instances.
    Currently it only support Computation values
    (used for setting lower and upper limits)
    """
    def __init__(self) -> None:
        self.computations: list['Computation'] = []


# Computation


class Computation:
    """
    Computation base class
    """
    def __init__(self) -> None:
        self._lower_limit: int | None = None
        self._upper_limit: int | None = None

    @property
    def lower_limit(self) -> int | None:
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, lower_limit: int | None) -> None:
        if lower_limit is None:
            self._lower_limit = None
        else:
            self._lower_limit = int(lower_limit)

    @property
    def upper_limit(self) -> int | None:
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, upper_limit: int | None) -> None:
        if upper_limit is None:
            self._upper_limit = None
        else:
            self._upper_limit = int(upper_limit)


class ValueTable(Computation):
    """
    A ValueTable is similar to an enumeration declaration
    """
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def append(self, value: str) -> None:
        self.values.append(value)

    def __getitem__(self, index: int) -> str:
        return self.values[index]


class RationalScaling(Computation):
    """
    A rational scaling defines a scaling based on offset and
    a scaling factor.
    """
    def __init__(self) -> None:
        super().__init__()
        self._offset: float = 0.0
        self._numerator: int = 1
        self._denominator: int = 0
        self._unit: str | None = None

    @property
    def offset(self) -> float:
        return self._offset

    @offset.setter
    def offset(self, value: int | float) -> None:
        self._offset = float(value)

    @property
    def numerator(self) -> int:
        return self._numerator

    @numerator.setter
    def numerator(self, value: int) -> None:
        self._numerator = int(value)

    @property
    def denominator(self) -> int:
        return self._denominator

    @denominator.setter
    def denominator(self, value: int) -> None:
        self._denominator = int(value)

    @property
    def unit(self) -> str | None:
        return self._unit

    @unit.setter
    def unit(self, value: str | None) -> None:
        if value is None:
            self._unit = None
        else:
            self._unit = str(value)


# --- Data Element


class DataElement:
    """
    A data element is a primitive part of a type definition
    """
    def __init__(self, type_code: apx_base.TypeCode) -> None:
        self.name: str | None = None
        self.type_code: apx_base.TypeCode = type_code
        self.lower_limit: int | None = None
        self.upper_limit: int | None = None
        self.array_len: int | None = None
        self.is_dynamic_array: bool = False
        if type_code == apx_base.TypeCode.RECORD:
            self.elements: list['DataElement'] | None = []
        else:
            self.elements = None
        self._typeref: "int | str | DataType | None" = None

    @property
    def has_limits(self) -> bool:
        return self.lower_limit is not None

    @property
    def is_array(self) -> bool:
        return self.array_len is not None

    @property
    def typeref(self) -> "int | str | DataType | None":
        return self._typeref

    @property
    def has_scalar_type_code(self) -> bool:
        return self.type_code not in [apx_base.TypeCode.NONE,
                                      apx_base.TypeCode.RECORD,
                                      apx_base.TypeCode.TYPE_REF_ID,
                                      apx_base.TypeCode.TYPE_REF_NAME,
                                      apx_base.TypeCode.TYPE_REF_PTR]

    @property
    def has_string_type_code(self) -> bool:
        return self.type_code in [apx_base.TypeCode.CHAR,
                                  apx_base.TypeCode.CHAR8,
                                  apx_base.TypeCode.CHAR16,
                                  apx_base.TypeCode.CHAR32]

    @typeref.setter
    def typeref(self, value: "int | str | DataType") -> None:
        if isinstance(value, int):
            self.type_code = apx_base.TypeCode.TYPE_REF_ID
        elif isinstance(value, str):
            self.type_code = apx_base.TypeCode.TYPE_REF_NAME
        elif isinstance(value, DataType):
            self.type_code = apx_base.TypeCode.TYPE_REF_PTR
        else:
            raise ValueError(type(value))
        self._typeref = value

    def set_limits(self, lower_limit: int, upper_limit: int) -> None:
        if lower_limit is None or upper_limit is None:
            raise ValueError("A 'None' Argument is not allowed")
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def get_limits(self) -> tuple[int | None, int | None]:
        return self.lower_limit, self.upper_limit

    def append(self, child_element: 'DataElement') -> None:
        assert self.elements is not None
        self.elements.append(child_element)

    def follow_type_references(self, data_type_list: list['DataType'],
                               data_type_map: dict[str, 'DataType']) -> apx_base.Result:
        """
        If data element is of type reference-by-name or reference-by-id,
        Transform it into reference-by-ptr by performing type lookups
        """
        if self.type_code == apx_base.TypeCode.RECORD:
            assert self.elements is not None
            for child_element in self.elements:
                result = child_element.follow_type_references(data_type_list, data_type_map)
                if result != apx_base.NO_ERROR:
                    return result
        elif self.type_code == apx_base.TypeCode.TYPE_REF_ID:
            assert isinstance(self.typeref, int)
            type_index = self.typeref
            if type_index >= len(data_type_list):
                return apx_base.INVALID_TYPE_REF_ERROR
            data_type = data_type_list[type_index]
            result = data_type.follow_type_references(data_type_list, data_type_map)
            if result != apx_base.NO_ERROR:
                return result
            self.typeref = data_type
        elif self.type_code == apx_base.TypeCode.TYPE_REF_NAME:
            assert isinstance(self.typeref, str)
            type_name = self.typeref
            data_type = data_type_map.get(type_name, None)
            if data_type is None:
                return apx_base.INVALID_TYPE_REF_ERROR
            result = data_type.follow_type_references(data_type_list, data_type_map)
            if result != apx_base.NO_ERROR:
                return result
            self.typeref = data_type
        # No other type codes needs special handling
        return apx_base.NO_ERROR

    def create_effective_element(self) -> tuple[apx_base.Result, 'DataElement | None']:
        """
        If DataElement is of basic type this method will create a clone.
        If DataElement is of record type it will create a clone where each element
        has been derived into its effective form.
        If DataElement is a type reference it will follow that reference until it finds its effective element.
        """
        assert self.type_code not in (apx_base.TypeCode.TYPE_REF_NAME, apx_base.TypeCode.TYPE_REF_ID)
        if self.type_code == apx_base.TypeCode.TYPE_REF_PTR:
            data_type = self.typeref
            assert isinstance(data_type, DataType)
            result, effective_element = data_type.create_effective_element()
            if result != apx_base.NO_ERROR or effective_element is None:
                return result, None
            if self.name is not None:
                effective_element.name = self.name
            if self.array_len is not None:  # Is this an array-type-reference?
                # The effective element will inherit array properties of its parent/self
                if effective_element.array_len is not None:
                    # Array of Array is not supported in aPX
                    return apx_base.UNSUPPORTED_ERROR, None
                else:
                    effective_element.array_len = self.array_len
                    effective_element.is_dynamic_array = self.is_dynamic_array
            return result, effective_element
        else:
            effective_element = self._shallow_copy()
            if self.type_code == apx_base.TypeCode.RECORD:
                assert self.elements is not None
                assert effective_element.elements is not None
                for child_element in self.elements:
                    result, effective_child_element = child_element.create_effective_element()
                    if result == apx_base.NO_ERROR and effective_child_element is not None:
                        effective_element.elements.append(effective_child_element)
                    else:
                        return result, None
            return apx_base.NO_ERROR, effective_element

    def derive_proper_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        type_code = self.type_code
        # This should only be used on effective data elements. No references allowed
        assert type_code not in [
            apx_base.TypeCode.NONE,
            apx_base.TypeCode.TYPE_REF_ID,
            apx_base.TypeCode.TYPE_REF_NAME,
            apx_base.TypeCode.TYPE_REF_PTR,
        ]
        if type_code == apx_base.TypeCode.RECORD:
            if self.is_array:
                return self._derive_array_of_records_init_value(parsed_init_value)
            else:
                return self._derive_record_init_value(parsed_init_value)
        elif self.is_array:
            return self._derive_array_init_value(parsed_init_value)
        else:
            return self._derive_scalar_init_value(parsed_init_value)

    def _shallow_copy(self) -> 'DataElement':
        clone = DataElement(self.type_code)
        clone.name = self.name
        clone.lower_limit = self.lower_limit
        clone.upper_limit = self.upper_limit
        clone.array_len = self.array_len
        clone.is_dynamic_array = self.is_dynamic_array
        return clone

    def _derive_array_of_records_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        derived_init_value = None
        if not isinstance(parsed_init_value, list):
            return apx_base.VALUE_TYPE_ERROR, None
        if self.is_dynamic_array:
            if len(parsed_init_value) == 0:
                derived_init_value = []
            else:
                # Only empty initializers are supported for dynamic arrays
                return apx_base.NOT_IMPLEMENTED_ERROR, None
        else:
            # Fixed-sized array of records
            derived_init_value = []
            if len(parsed_init_value) != self.array_len:
                return apx_base.VALUE_LENGTH_ERROR, None
            for child_parsed_value in parsed_init_value:
                if not isinstance(child_parsed_value, list):
                    return apx_base.VALUE_TYPE_ERROR, None
                result, child_init_value = self._derive_dict_init_value(child_parsed_value)
                if result == apx_base.NO_ERROR:
                    assert child_init_value is not None
                    derived_init_value.append(child_init_value)
                else:
                    return result, None
        return apx_base.NO_ERROR, derived_init_value

    def _derive_record_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        if not isinstance(parsed_init_value, list):
            return apx_base.VALUE_TYPE_ERROR, None
        return self._derive_dict_init_value(parsed_init_value)

    def _derive_array_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        if self.has_string_type_code and is_scalar_value(parsed_init_value):
            return self._derive_string_init_value(parsed_init_value)
        if not isinstance(parsed_init_value, list):
            return apx_base.VALUE_TYPE_ERROR, None
        if self.is_dynamic_array:
            if len(parsed_init_value) == 0:
                derived_init_value = []
            else:
                # Only empty initializers are supported for dynamic arrays
                return apx_base.NOT_IMPLEMENTED_ERROR, None
        else:
            derived_init_value = []
            if len(parsed_init_value) != self.array_len:
                return apx_base.VALUE_LENGTH_ERROR, None
            if self.has_scalar_type_code:
                for child_parsed_value in parsed_init_value:
                    if is_scalar_value(child_parsed_value):
                        derived_init_value.append(child_parsed_value)
                    else:
                        return apx_base.VALUE_TYPE_ERROR, None
            else:
                return apx_base.NOT_IMPLEMENTED_ERROR, None
        return apx_base.NO_ERROR, derived_init_value

    def _derive_string_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        if isinstance(parsed_init_value, str):
            if self.type_code == apx_base.TypeCode.CHAR:
                # TODO: verify ascii-characaters
                return apx_base.NO_ERROR, parsed_init_value
            if self.type_code == apx_base.TypeCode.CHAR8:
                # TODO: verify utf8-characaters
                return apx_base.NO_ERROR, parsed_init_value
            if self.type_code == apx_base.TypeCode.CHAR16:
                return apx_base.NOT_IMPLEMENTED_ERROR, None
            if self.type_code == apx_base.TypeCode.CHAR32:
                return apx_base.NOT_IMPLEMENTED_ERROR, None
        return apx_base.VALUE_TYPE_ERROR, None

    def _derive_scalar_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        if is_scalar_value(parsed_init_value):
            return apx_base.NO_ERROR, parsed_init_value
        return apx_base.VALUE_TYPE_ERROR, None

    def _derive_dict_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        derived_init_value = {}
        if not isinstance(parsed_init_value, list):
            return apx_base.VALUE_TYPE_ERROR, None
        assert self.elements is not None
        if len(self.elements) != len(parsed_init_value):
            return apx_base.VALUE_LENGTH_ERROR, None
        for i, child_element in enumerate(self.elements):
            child_parsed_init_value = parsed_init_value[i]
            result, child_derived_init_value = child_element.derive_proper_init_value(child_parsed_init_value)
            if result != apx_base.NO_ERROR:
                return result, None
            derived_init_value[child_element.name] = child_derived_init_value
        return apx_base.NO_ERROR, derived_init_value


# Signature


class DataSignature:
    def __init__(self) -> None:
        self.element: 'DataElement | None' = None
        self.effective_element: 'DataElement | None' = None

    def follow_type_references(self, data_type_list: list['DataType'],
                               data_type_map: dict[str, 'DataType']) -> apx_base.Result:
        if self.element is None:
            return apx_base.NO_ERROR
        return self.element.follow_type_references(data_type_list, data_type_map)

    def create_effective_element(self) -> tuple[apx_base.Result, 'DataElement | None']:
        if self.element is None:
            return apx_base.NULL_PTR_ERROR, None
        result, effective_element = self.element.create_effective_element()
        if result == apx_base.NO_ERROR:
            self.effective_element = effective_element
        return result, effective_element

    def derive_proper_init_value(self, parsed_init_value: Any) -> tuple[apx_base.Result, Any]:
        if self.effective_element is None:
            return apx_base.NULL_PTR_ERROR, None
        return self.effective_element.derive_proper_init_value(parsed_init_value)


# Data Type


class DataType:
    def __init__(self, name: str, line_number: int | None = None) -> None:
        self.name: str = name
        self.line_number: int | None = line_number
        self.dsg: DataSignature = DataSignature()
        self.type_id: int = apx_base.INVALID_ID
        self._attr: 'TypeAttributes | None' = None

    @property
    def attributes(self) -> 'TypeAttributes | None':
        return self._attr

    @attributes.setter
    def attributes(self, value: 'TypeAttributes | None') -> None:
        if value is not None:
            assert isinstance(value, TypeAttributes)
        self._attr = value

    @property
    def has_attributes(self) -> bool:
        return self.attributes is not None

    @property
    def data_element(self) -> 'DataElement | None':
        return self.dsg.element

    @data_element.setter
    def data_element(self, element: 'DataElement') -> None:
        assert isinstance(element, DataElement)
        self.dsg.element = element

    def follow_type_references(self, data_type_list: list['DataType'],
                               data_type_map: dict[str, 'DataType']) -> apx_base.Result:
        return self.dsg.follow_type_references(data_type_list, data_type_map)

    def create_effective_element(self) -> tuple[apx_base.Result, 'DataElement | None']:
        return self.dsg.create_effective_element()


# Port


class Port:
    """
    APX port base class
    """
    def __init__(self, port_type: apx_base.PortType, name: str, line_number: int | None = None) -> None:
        self.port_type: apx_base.PortType = port_type
        self.name: str = name
        self.line_number: int | None = line_number
        self.dsg: DataSignature = DataSignature()
        self.type_id: int = apx_base.INVALID_ID
        self.proper_init_value: Any = None
        self._attr: 'PortAttributes | None' = None

    @property
    def attributes(self) -> 'PortAttributes | None':
        return self._attr

    @attributes.setter
    def attributes(self, value: 'PortAttributes | None') -> None:
        if value is not None:
            assert isinstance(value, PortAttributes)
        self._attr = value

    @property
    def has_attributes(self) -> bool:
        return self.attributes is not None

    @property
    def data_element(self) -> 'DataElement | None':
        return self.dsg.element

    @data_element.setter
    def data_element(self, element: 'DataElement') -> None:
        assert isinstance(element, DataElement)
        self.dsg.element = element

    @property
    def queue_len(self) -> int:
        if self.attributes is not None:
            return self.attributes.queue_length
        return 0

    @property
    def effective_element(self) -> 'DataElement | None':
        return self.dsg.effective_element

    def follow_type_references(self, data_type_list: list['DataType'],
                               data_type_map: dict[str, 'DataType']) -> apx_base.Result:
        return self.dsg.follow_type_references(data_type_list, data_type_map)

    def create_effective_element(self) -> apx_base.Result:
        result, _unused = self.dsg.create_effective_element()
        return result

    def derive_proper_init_value(self) -> apx_base.Result:
        if self.attributes is not None:
            if self.attributes.has_init_value:
                result, proper_init_value = self.dsg.derive_proper_init_value(self.attributes.init_value)
                if result == apx_base.NO_ERROR:
                    self.proper_init_value = proper_init_value
                else:
                    return result
        return apx_base.NO_ERROR


class RequirePort(Port):
    """
    APX require port class
    """
    def __init__(self, name: str, line_number: int | None = None) -> None:
        super().__init__(apx_base.PortType.REQUIRE, name, line_number)


class ProvidePort(Port):
    """
    APX provide port class
    """
    def __init__(self, name: str, line_number: int | None = None) -> None:
        super().__init__(apx_base.PortType.PROVIDE, name, line_number)


# Node


class Node:
    """
    APX Node class
    """
    def __init__(self, name: str, line_number: int | None = None) -> None:
        self.name: str = str(name)
        self.is_finalized: bool = False
        self.data_types: list['DataType'] = []
        self.require_ports: list['RequirePort'] = []
        self.provide_ports: list['ProvidePort'] = []
        self.port_map: dict[str, 'Port'] = {}
        self.data_type_map: dict[str, 'DataType'] = {}
        self.node_parser: Any = None
        self.line_number: int | None = line_number  # Line number where node definition starts
        self.last_error_line: int | None = None

    def append(self, item: 'DataType | RequirePort | ProvidePort') -> 'DataType | RequirePort | ProvidePort':
        """
        Adds the item to the node.
        Item can be of type DataType, RequirePort and ProvidePort
        returns the object (port or datatype)
        """
        if isinstance(item, DataType):
            return self.add_data_type(item)
        elif isinstance(item, RequirePort):
            return self.add_require_port(item)
        elif isinstance(item, ProvidePort):
            return self.add_provide_port(item)
        else:
            raise ValueError("Unsupported argument type: " + str(type(item)))

    def add_data_type(self, data_type: 'DataType') -> 'DataType':
        if data_type.name not in self.data_type_map:
            self.data_types.append(data_type)
            self.data_type_map[data_type.name] = data_type
        else:
            raise apx_base.DataTypeAlreadyExists(data_type.name)
        return data_type

    def add_require_port(self, port: 'RequirePort') -> 'RequirePort':
        if port.name not in self.port_map:
            self.port_map[port.name] = port
            self.require_ports.append(port)
        else:
            raise apx_base.PortAlreadyExists(port.name)
        return port

    def add_provide_port(self, port: 'ProvidePort') -> 'ProvidePort':
        if port.name not in self.port_map:
            self.port_map[port.name] = port
            self.provide_ports.append(port)
        else:
            raise apx_base.PortAlreadyExists(port.name)
        return port

    def finalize(self) -> apx_base.Result:
        if self.is_finalized:
            return apx_base.NO_ERROR
        result = self._follow_type_references_on_ports(self.provide_ports + self.require_ports)
        if result != apx_base.NO_ERROR:
            return result
        result = self._create_effective_elements_on_ports(self.provide_ports + self.require_ports)
        if result != apx_base.NO_ERROR:
            return result
        result = self._derive_proper_init_values_on_ports(self.provide_ports + self.require_ports)
        if result != apx_base.NO_ERROR:
            return result
        self.is_finalized = True
        return apx_base.NO_ERROR

    def _follow_type_references_on_ports(self, ports: list['Port']) -> apx_base.Result:
        for port in ports:
            result = port.follow_type_references(self.data_types, self.data_type_map)
            if result != apx_base.NO_ERROR:
                self.last_error_line = port.line_number
                return result
        return apx_base.NO_ERROR

    def _create_effective_elements_on_ports(self, ports: list['Port']) -> apx_base.Result:
        for port in ports:
            result = port.create_effective_element()
            if result != apx_base.NO_ERROR:
                self.last_error_line = port.line_number
                return result
        return apx_base.NO_ERROR

    def _derive_proper_init_values_on_ports(self, ports: list['Port']) -> apx_base.Result:
        for port in ports:
            result = port.derive_proper_init_value()
            if result != apx_base.NO_ERROR:
                self.last_error_line = port.line_number
                return result
        return apx_base.NO_ERROR
