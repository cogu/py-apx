"""
Common definitions
"""
from enum import Enum

# Constants

INT8_MIN = -128
INT16_MIN = -32768
INT32_MIN = -2147483648
INT64_MIN = -9223372036854775808
INT8_MAX = 127
INT16_MAX = 32767
INT32_MAX = 2147483647
INT64_MAX = 9223372036854775807
UINT8_MAX = 255
UINT16_MAX = 65535
UINT32_MAX = 4294967295
UINT64_MAX = 18446744073709551615
UINT8_SIZE = 1
UINT16_SIZE = 2
UINT32_SIZE = 4
UINT64_SIZE = 8
INT8_SIZE = 1
INT16_SIZE = 2
INT32_SIZE = 4
INT64_SIZE = 8
CHAR_SIZE = 1
CHAR8_SIZE = 1
CHAR16_SIZE = 2
CHAR32_SIZE = 2
BOOL_SIZE = 1
BYTE_SIZE = 1
INSTR_SIZE = 1
INVALID_ID = -1
INVALID_TYPE_ID = -1


# Enumerations

class Result(Enum):
    """
    Result codes
    """
    NO_ERROR = 0
    INVALID_ARGUMENT_ERROR = 1
    MEM_ERROR = 2
    PARSE_ERROR = 3
    DATA_SIGNATURE_ERROR = 4
    PORT_SIGNATURE_ERROR = 5
    INTERNAL_ERROR = 6
    LENGTH_ERROR = 7
    ELEMENT_TYPE_ERROR = 8
    UNSUPPORTED_ERROR = 10
    NOT_IMPLEMENTED_ERROR = 11
    NOT_FOUND_ERROR = 12
    UNMATCHED_BRACE_ERROR = 13
    UNMATCHED_BRACKET_ERROR = 14
    UNMATCHED_STRING_ERROR = 15
    INVALID_TYPE_REF_ERROR = 16
    EXPECTED_BRACKET_ERROR = 17
    INVALID_ATTRIBUTE_ERROR = 18
    TOO_MANY_NODES_ERROR = 19
    NODE_MISSING_ERROR = 20
    NODE_ALREADY_EXISTS_ERROR = 21
    TYPE_ALREADY_EXIST_ERROR = 22
    PORT_ALREADY_EXIST_ERROR = 23
    FILE_ALREADY_EXISTS_ERROR = 24
    MISSING_BUFFER_ERROR = 25
    MISSING_FILE_ERROR = 26
    NAME_MISSING_ERROR = 27
    NAME_TOO_LONG_ERROR = 28
    THREAD_CREATE_ERROR = 29
    THREAD_JOIN_ERROR = 30
    THREAD_JOIN_TIMEOUT_ERROR = 31
    FILE_TOO_LARGE_ERROR = 32
    MSG_TOO_LARGE_ERROR = 33
    CONNECTION_ERROR = 34
    TRANSMIT_ERROR = 35
    NULL_PTR_ERROR = 36
    BUFFER_BOUNDARY_ERROR = 37
    BUFFER_FULL_ERROR = 38
    QUEUE_FULL_ERROR = 39
    DATA_NOT_PROCESSED_ERROR = 40
    PACK_ERROR = 41
    UNPACK_ERROR = 42
    READ_ERROR = 43
    INVALID_MSG_ERROR = 44
    UNEXPECTED_DATA_ERROR = 45
    INVALID_PROGRAM_ERROR = 46
    INVALID_STATE_ERROR = 47
    INVALID_INSTRUCTION_ERROR = 48
    FILE_NOT_FOUND_ERROR = 49
    MISSING_KEY_ERROR = 50
    INVALID_OPEN_HANDLER_ERROR = 51
    INVALID_WRITE_HANDLER_ERROR = 52
    INVALID_WRITE_ERROR = 53
    INVALID_FILE_ERROR = 54
    INIT_VALUE_ERROR = 55
    INVALID_ADDRESS_ERROR = 56
    FILE_NOT_OPEN_ERROR = 57
    BUSY_ERROR = 58
    DATA_NOT_COMPLETE_ERROR = 59
    NOT_CONNECTED_ERROR = 60
    INVALID_NAME_ERROR = 61
    INVALID_PORT_HANDLE_ERROR = 62
    STRAY_CHARACTERS_AFTER_PARSE_ERROR = 63
    EMPTY_RECORD_ERROR = 64
    INVALID_HEADER_ERROR = 65
    UNEXPECTED_END_ERROR = 66
    VALUE_TYPE_ERROR = 67
    VALUE_RANGE_ERROR = 68
    VALUE_CONVERSION_ERROR = 69
    VALUE_LENGTH_ERROR = 70
    NUMBER_TOO_LARGE_ERROR = 71
    VERSION_ERROR = 72
    TOO_MANY_PORTS_ERROR = 73
    FILE_CREATE_ERROR = 74
    BUFFER_TOO_SMALL_ERROR = 75
    NO_VALUE_ERROR = 76


class PortType(Enum):
    """
    Port types
    """
    REQUIRE = 0
    PROVIDE = 1
    PROVIDE_REQUIRE = 2  # Reserved for future use


class SizeType(Enum):
    """
    Size types used for dynamic arrays
    """
    UINT8 = 0
    UINT16 = 1
    UINT32 = 2
    UNSUPPORTED = 3


class TypeCode(Enum):
    """
    Type codes
    """
    NONE = 0
    UINT8 = 1
    UINT16 = 2
    UINT32 = 3
    UINT64 = 4
    INT8 = 5
    INT16 = 6
    INT32 = 7
    INT64 = 8
    CHAR = 9
    CHAR8 = 10
    CHAR16 = 11  # RESERVED FOR APX IDL v1.4
    CHAR32 = 12  # RESERVED FOR APX IDL v1.4
    BOOL = 13
    BYTE = 14
    RECORD = 15
    TYPE_REF_ID = 16
    TYPE_REF_NAME = 17
    TYPE_REF_PTR = 18

# More constants


SIZE_TYPE_SIZE = [UINT8_SIZE,
                  UINT16_SIZE,
                  UINT32_SIZE,
                  None]

NO_ERROR = Result.NO_ERROR
INVALID_ARGUMENT_ERROR = Result.INVALID_ARGUMENT_ERROR
MEM_ERROR = Result.MEM_ERROR
PARSE_ERROR = Result.PARSE_ERROR
DATA_SIGNATURE_ERROR = Result.DATA_SIGNATURE_ERROR
PORT_SIGNATURE_ERROR = Result.PORT_SIGNATURE_ERROR
INTERNAL_ERROR = Result.INTERNAL_ERROR
LENGTH_ERROR = Result.LENGTH_ERROR
ELEMENT_TYPE_ERROR = Result.ELEMENT_TYPE_ERROR
UNSUPPORTED_ERROR = Result.UNSUPPORTED_ERROR
NOT_IMPLEMENTED_ERROR = Result.NOT_IMPLEMENTED_ERROR
NOT_FOUND_ERROR = Result.NOT_FOUND_ERROR
UNMATCHED_BRACE_ERROR = Result.UNMATCHED_BRACE_ERROR
UNMATCHED_BRACKET_ERROR = Result.UNMATCHED_BRACKET_ERROR
UNMATCHED_STRING_ERROR = Result.UNMATCHED_STRING_ERROR
INVALID_TYPE_REF_ERROR = Result.INVALID_TYPE_REF_ERROR
EXPECTED_BRACKET_ERROR = Result.EXPECTED_BRACKET_ERROR
INVALID_ATTRIBUTE_ERROR = Result.INVALID_ATTRIBUTE_ERROR
TOO_MANY_NODES_ERROR = Result.TOO_MANY_NODES_ERROR
NODE_MISSING_ERROR = Result.NODE_MISSING_ERROR
NODE_ALREADY_EXISTS_ERROR = Result.NODE_ALREADY_EXISTS_ERROR
TYPE_ALREADY_EXIST_ERROR = Result.TYPE_ALREADY_EXIST_ERROR
PORT_ALREADY_EXIST_ERROR = Result.PORT_ALREADY_EXIST_ERROR
FILE_ALREADY_EXISTS_ERROR = Result.FILE_ALREADY_EXISTS_ERROR
MISSING_BUFFER_ERROR = Result.MISSING_BUFFER_ERROR
MISSING_FILE_ERROR = Result.MISSING_FILE_ERROR
NAME_MISSING_ERROR = Result.NAME_MISSING_ERROR
NAME_TOO_LONG_ERROR = Result.NAME_TOO_LONG_ERROR
THREAD_CREATE_ERROR = Result.THREAD_CREATE_ERROR
THREAD_JOIN_ERROR = Result.THREAD_JOIN_ERROR
THREAD_JOIN_TIMEOUT_ERROR = Result.THREAD_JOIN_TIMEOUT_ERROR
FILE_TOO_LARGE_ERROR = Result.FILE_TOO_LARGE_ERROR
MSG_TOO_LARGE_ERROR = Result.MSG_TOO_LARGE_ERROR
CONNECTION_ERROR = Result.CONNECTION_ERROR
TRANSMIT_ERROR = Result.TRANSMIT_ERROR
NULL_PTR_ERROR = Result.NULL_PTR_ERROR
BUFFER_BOUNDARY_ERROR = Result.BUFFER_BOUNDARY_ERROR
BUFFER_FULL_ERROR = Result.BUFFER_FULL_ERROR
QUEUE_FULL_ERROR = Result.QUEUE_FULL_ERROR
DATA_NOT_PROCESSED_ERROR = Result.DATA_NOT_PROCESSED_ERROR
PACK_ERROR = Result.PACK_ERROR
UNPACK_ERROR = Result.UNPACK_ERROR
READ_ERROR = Result.READ_ERROR
INVALID_MSG_ERROR = Result.INVALID_MSG_ERROR
UNEXPECTED_DATA_ERROR = Result.UNEXPECTED_DATA_ERROR
INVALID_PROGRAM_ERROR = Result.INVALID_PROGRAM_ERROR
INVALID_STATE_ERROR = Result.INVALID_STATE_ERROR
INVALID_INSTRUCTION_ERROR = Result.INVALID_INSTRUCTION_ERROR
FILE_NOT_FOUND_ERROR = Result.FILE_NOT_FOUND_ERROR
MISSING_KEY_ERROR = Result.MISSING_KEY_ERROR
INVALID_OPEN_HANDLER_ERROR = Result.INVALID_OPEN_HANDLER_ERROR
INVALID_WRITE_HANDLER_ERROR = Result.INVALID_WRITE_HANDLER_ERROR
INVALID_WRITE_ERROR = Result.INVALID_WRITE_ERROR
INVALID_FILE_ERROR = Result.INVALID_FILE_ERROR
INIT_VALUE_ERROR = Result.INIT_VALUE_ERROR
INVALID_ADDRESS_ERROR = Result.INVALID_ADDRESS_ERROR
FILE_NOT_OPEN_ERROR = Result.FILE_NOT_OPEN_ERROR
BUSY_ERROR = Result.BUSY_ERROR
DATA_NOT_COMPLETE_ERROR = Result.DATA_NOT_COMPLETE_ERROR
NOT_CONNECTED_ERROR = Result.NOT_CONNECTED_ERROR
INVALID_NAME_ERROR = Result.INVALID_NAME_ERROR
INVALID_PORT_HANDLE_ERROR = Result.INVALID_PORT_HANDLE_ERROR
STRAY_CHARACTERS_AFTER_PARSE_ERROR = Result.STRAY_CHARACTERS_AFTER_PARSE_ERROR
EMPTY_RECORD_ERROR = Result.EMPTY_RECORD_ERROR
INVALID_HEADER_ERROR = Result.INVALID_HEADER_ERROR
UNEXPECTED_END_ERROR = Result.UNEXPECTED_END_ERROR
VALUE_TYPE_ERROR = Result.VALUE_TYPE_ERROR
VALUE_RANGE_ERROR = Result.VALUE_RANGE_ERROR
VALUE_CONVERSION_ERROR = Result.VALUE_CONVERSION_ERROR
VALUE_LENGTH_ERROR = Result.VALUE_LENGTH_ERROR
NUMBER_TOO_LARGE_ERROR = Result.NUMBER_TOO_LARGE_ERROR
NO_VALUE_ERROR = Result.NO_VALUE_ERROR


# Exceptions

class DataTypeAlreadyExists(RuntimeError):
    pass


class PortAlreadyExists(RuntimeError):
    pass


class ParseError(RuntimeError):
    pass


class ValueTypeError(ValueError):
    pass


class ValueRangeError(ValueError):
    pass


# The purpose for below classes are for making the end user API easy to use.
# They do not represent actual ports or data types, those are defined by the classes in the apx.model package.

class Port:
    """
    APX Pseudo-port base class
    """
    def __init__(self, port_type: PortType | int, name: str, data_signature: str,
                 attributes: str | None = None) -> None:
        self.port_type: PortType | int = port_type
        self.name: str = name
        self.dsg: str = data_signature
        self.attributes: str | None = attributes


class RequirePort(Port):
    """
    APX require-port pseudo-class
    """
    def __init__(self, name: str, data_signature: str, attributes: str | None = None) -> None:
        super().__init__(PortType.REQUIRE, name, data_signature, attributes)


class ProvidePort(Port):
    """
    APX provide-port pseudo-class
    """
    def __init__(self, name: str, data_signature: str, attributes: str | None = None) -> None:
        super().__init__(PortType.PROVIDE, name, data_signature, attributes)


class DataType:
    """
    APX datatype pseudo-class
    """
    def __init__(self, name: str, data_signature: str, attributes: str | None = None) -> None:
        self.name: str = name
        self.dsg: str = data_signature
        self.attributes: str | None = attributes


class Node:
    """
    APX Node pseudo-class
    """
    def __init__(self, name: str) -> None:
        self.name: str = str(name)
        self.is_finalized: bool = False
        self.data_types: list[DataType] = []
        self.require_ports: list[RequirePort] = []
        self.provide_ports: list[ProvidePort] = []
        self.port_map: dict[str, Port] = {}
        self.data_type_map: dict[str, DataType] = {}

    def append(self, item: DataType | RequirePort | ProvidePort) -> DataType | RequirePort | ProvidePort:
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

    def add_data_type(self, data_type: DataType) -> DataType:
        if data_type.name not in self.data_type_map:
            self.data_types.append(data_type)
            self.data_type_map[data_type.name] = data_type
        else:
            raise DataTypeAlreadyExists(data_type.name)
        return data_type

    def add_require_port(self, port: RequirePort) -> RequirePort:
        if port.name not in self.port_map:
            self.port_map[port.name] = port
            self.require_ports.append(port)
        else:
            raise PortAlreadyExists(port.name)
        return port

    def add_provide_port(self, port: ProvidePort) -> ProvidePort:
        if port.name not in self.port_map:
            self.port_map[port.name] = port
            self.provide_ports.append(port)
        else:
            raise PortAlreadyExists(port.name)
        return port
