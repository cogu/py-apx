"""
Signature parser for APX data elements and signatures
"""
from dataclasses import dataclass
from enum import Enum
import re
from typing import Callable
import apx.base as apx_base
import apx.model as apx_model
from apx.parser.base import BaseParser


class TokenClass(Enum):
    """
    Parser token class
    """
    RECORD_DECLARATION = 1
    GROUP_DECLARATION = 2
    FUNCTION_DECLARATION = 3
    DATA_ELEMENT = 4


TYPE_CODE_CHAR_MAP = [
    '{',
    '[',
    '(',
    'T',
    'a',
    'A',
    'b',
    'B',
    'c',
    'C',
    'l',
    'L',
    'q',
    'Q',
    's',
    'S',
    'u',
    'U',
]

PARSER_TOKEN_CLASS_MAP = [
    TokenClass.RECORD_DECLARATION,    # {
    TokenClass.GROUP_DECLARATION,     # [
    TokenClass.FUNCTION_DECLARATION,  # (
    TokenClass.DATA_ELEMENT,          # T
    TokenClass.DATA_ELEMENT,          # a
    TokenClass.DATA_ELEMENT,          # A
    TokenClass.DATA_ELEMENT,          # b
    TokenClass.DATA_ELEMENT,          # B
    TokenClass.DATA_ELEMENT,          # c
    TokenClass.DATA_ELEMENT,          # C
    TokenClass.DATA_ELEMENT,          # l
    TokenClass.DATA_ELEMENT,          # L
    TokenClass.DATA_ELEMENT,          # q
    TokenClass.DATA_ELEMENT,          # Q
    TokenClass.DATA_ELEMENT,          # s
    TokenClass.DATA_ELEMENT,          # S
    TokenClass.DATA_ELEMENT,          # u
    TokenClass.DATA_ELEMENT,          # U
]

PARSER_TYPE_CODE_MAP = [
    apx_base.TypeCode.RECORD,       # {
    apx_base.TypeCode.NONE,         # [
    apx_base.TypeCode.NONE,         # (
    apx_base.TypeCode.TYPE_REF_ID,  # T
    apx_base.TypeCode.CHAR,         # a
    apx_base.TypeCode.CHAR8,        # A
    apx_base.TypeCode.BOOL,         # b
    apx_base.TypeCode.BYTE,         # B
    apx_base.TypeCode.INT8,         # c
    apx_base.TypeCode.UINT8,        # C
    apx_base.TypeCode.INT32,        # l
    apx_base.TypeCode.UINT32,       # L
    apx_base.TypeCode.INT64,        # q
    apx_base.TypeCode.UINT64,       # Q
    apx_base.TypeCode.INT16,        # s
    apx_base.TypeCode.UINT16,       # S
    apx_base.TypeCode.CHAR16,       # u
    apx_base.TypeCode.CHAR32,       # U
]

SIGNED_TYPE_MAP = [
    False,  # {
    False,  # [
    False,  # (
    False,  # T
    True,   # a
    False,  # A
    False,  # b
    False,  # B
    True,   # c
    False,  # C
    True,   # l
    False,  # L
    True,   # q
    False,  # Q
    True,   # s
    False,  # S
    False,  # u
    False,  # U
]

CHECK_LIMITS = [
    False,  # {
    False,  # [
    False,  # (
    False,  # T
    False,  # a
    False,  # A
    False,  # b
    True,   # B
    True,   # c
    True,   # C
    True,   # l
    True,   # L
    True,   # q
    True,   # Q
    True,   # s
    True,   # S
    False,  # u
    False,  # U
]


@dataclass
class SignatureParseState:
    """
    Internal parse state for SignatureParser.
    """
    is_record: bool = False
    data_element: apx_model.DataElement | None = None


class SignatureParser(BaseParser):
    """
    Parser for APX type signatures
    """

    def __init__(self) -> None:
        super().__init__()
        self.state: SignatureParseState | None = None
        self.array_re = re.compile(r'\[\s*([1-9][0-9]*)\*\s*\]|\[\s*([1-9][0-9]*)\s*\]')

    def take_data_element(self) -> apx_model.DataElement | None:
        """
        Takes the parsed data element from the parser state
        """
        if self.state is not None:
            retval = self.state.data_element
            self.state.data_element = None
            return retval
        return None

    def parse_signature(self, signature: str) -> apx_base.Result:
        """
        Parses a full data signature string
        """
        self.reset(signature)
        self.state = SignatureParseState()
        result = self.parse_data_element()
        if result == apx_base.Result.NO_ERROR:
            assert self.read_position is not None and self.input is not None
            if self.read_position != len(self.input):
                return self._error(apx_base.Result.STRAY_CHARACTERS_AFTER_PARSE_ERROR)
            return result
        else:
            return self._error(result)

    def parse_data_element(self) -> apx_base.Result:
        """
        Parses a single data element or record structure
        """
        assert self.state is not None
        element_name = None
        if self.state.is_record:
            result, element_name = self._parse_name()
            if result != apx_base.Result.NO_ERROR:
                return result
        c = self._next()
        try:
            i = TYPE_CODE_CHAR_MAP.index(c)
        except ValueError:
            assert self.read_position is not None
            self.read_position -= 1
            return apx_base.Result.PARSE_ERROR
        token_class = PARSER_TOKEN_CLASS_MAP[i]
        type_code = PARSER_TYPE_CODE_MAP[i]
        is_signed_type = SIGNED_TYPE_MAP[i]
        is_64_bit_type = bool(type_code in (apx_base.TypeCode.INT64, apx_base.TypeCode.UINT64))
        check_limits = CHECK_LIMITS[i]
        if token_class == TokenClass.DATA_ELEMENT:
            return self._parse_primitive_data_element(
                type_code, element_name, is_signed_type, is_64_bit_type, check_limits
            )
        if token_class == TokenClass.RECORD_DECLARATION:
            return self._parse_record_declaration(type_code, element_name)
        raise NotImplementedError(token_class)

    def _parse_primitive_data_element(self,
                                      type_code: apx_base.TypeCode,
                                      element_name: str | None,
                                      is_signed_type: bool,
                                      is_64_bit_type: bool,
                                      check_limits: bool) -> apx_base.Result:
        assert self.state is not None
        assert type_code != apx_base.TypeCode.NONE
        self.state.data_element = apx_model.DataElement(type_code)
        if element_name is not None:
            self.state.data_element.name = element_name
        if type_code == apx_base.TypeCode.TYPE_REF_ID:
            result = self._parse_type_reference()
            if result != apx_base.Result.NO_ERROR:
                return result
        if check_limits:
            if is_64_bit_type:
                result = self._parse_limits_i64() if is_signed_type else self._parse_limits_u64()
            else:
                result = self._parse_limits_i32() if is_signed_type else self._parse_limits_u32()
            if result != apx_base.Result.NO_ERROR:
                return result
        elif self._test_char('('):  # This typecode does not support limits
            return apx_base.Result.PARSE_ERROR
        return self._parse_array()

    def _parse_record_declaration(self,
                                  type_code: apx_base.TypeCode,
                                  element_name: str | None) -> apx_base.Result:
        assert self.state is not None
        self.state.data_element = apx_model.DataElement(type_code)
        if element_name is not None:
            self.state.data_element.name = element_name
        parent = self.state
        self.state = SignatureParseState(True)
        assert self.read_position is not None and self.input is not None
        while self.read_position < len(self.input):
            result = self.parse_data_element()
            if result != apx_base.Result.NO_ERROR:
                return result
            assert parent.data_element is not None and self.state.data_element is not None
            parent.data_element.append(self.state.data_element)
            self.state.data_element = None
            if self.read_position == len(self.input):
                # Expect signature to end with '}' character
                self.state = parent
                return apx_base.Result.PARSE_ERROR
            if self._match_char('}'):
                self.state = parent
                break
        return self._parse_array()

    def _parse_limits_helper(self, parse_fn: Callable[[], int | None]) -> apx_base.Result:
        if not self._test_char('('):
            return apx_base.Result.NO_ERROR
        self.read_position = (self.read_position or 0) + 1
        result = apx_base.Result.PARSE_ERROR
        if self._lstrip():
            lower_limit = parse_fn()
            if lower_limit is not None and self._lstrip() and self._match_char(','):
                if self._lstrip():
                    upper_limit = parse_fn()
                    if upper_limit is not None and self._lstrip() and self._match_char(')'):
                        assert self.state is not None and self.state.data_element is not None
                        self.state.data_element.set_limits(lower_limit, upper_limit)
                        result = apx_base.Result.NO_ERROR
        return result

    def _parse_limits_i64(self) -> apx_base.Result:
        return self._parse_limits_helper(self.parse_int64)

    def _parse_limits_u64(self) -> apx_base.Result:
        return self._parse_limits_helper(self.parse_uint64)

    def _parse_limits_u32(self) -> apx_base.Result:
        return self._parse_limits_helper(self.parse_uint32)

    def _parse_limits_i32(self) -> apx_base.Result:
        return self._parse_limits_helper(self.parse_int32)

    def _parse_array(self) -> apx_base.Result:
        if self._test_char('['):
            assert self.input is not None and self.read_position is not None
            tmp = self.input[self.read_position:]
            match = self.array_re.match(tmp)
            if match is not None:
                assert self.state is not None and self.state.data_element is not None
                if match.group(1) is not None:
                    self.state.data_element.array_len = int(match.group(1))
                    self.state.data_element.is_dynamic_array = True
                else:
                    self.state.data_element.array_len = int(match.group(2))
                self.read_position += len(match.group(0))
                return apx_base.Result.NO_ERROR
            return apx_base.Result.PARSE_ERROR
        return apx_base.Result.NO_ERROR

    def _parse_name(self) -> tuple[apx_base.Result, str | None]:
        return self.parse_string_literal()

    def _parse_type_reference(self) -> apx_base.Result:
        if self._match_char('['):
            if self._lstrip():
                result, name = self._parse_name()
                assert self.state is not None and self.state.data_element is not None
                if result == apx_base.Result.NO_ERROR:
                    self.state.data_element.typeref = name
                elif result == apx_base.Result.PARSE_ERROR:
                    value = self._parse_integer()
                    if value is None:
                        return apx_base.Result.PARSE_ERROR
                    self.state.data_element.typeref = value
                else:
                    return result
                if self._lstrip():
                    if self._match_char(']'):
                        return apx_base.Result.NO_ERROR
        return apx_base.Result.PARSE_ERROR
