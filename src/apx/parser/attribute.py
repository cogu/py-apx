"""
Attribute parser for APX port and type attributes
"""
from dataclasses import dataclass
from typing import Any
import re
import apx.base as apx_base
import apx.model as apx_model
from apx.parser.base import BaseParser


@dataclass
class AttributeParseState:
    parent: Any = None
    scalar_value: Any = None
    initializer_list: Any = None


class ComputationParseState:
    """
    State for computation parsing
    """

    def __init__(self) -> None:
        self._lower_limit: int | None = None
        self._upper_limit: int | None = None

    @property
    def lower_limit(self) -> int | None:
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, lower_limit: int | None) -> None:
        self._lower_limit = int(lower_limit) if lower_limit is not None else None

    @property
    def upper_limit(self) -> int | None:
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, upper_limit: int | None) -> None:
        self._upper_limit = int(upper_limit) if upper_limit is not None else None


class ValueTableParseState(ComputationParseState):
    """
    State for ValueTable parsing
    """

    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []
        self.arg_pos: int = 0
        self.last_was_string: bool = False


class RationalScalingParseState(ComputationParseState):
    """
    State for RationalScaling parsing
    """

    def __init__(self) -> None:
        super().__init__()
        self.offset: float = 0.0
        self.numerator: int = 0
        self.denominator: int = 0
        self.arg_pos: int = 0
        self.unit: str | None = None


VALUE_TABLE_ARG_TYPE_INVALID = 0
VALUE_TABLE_ARG_TYPE_INTEGER = 1
VALUE_TABLE_ARG_TYPE_STRING_LITERAL = 2

TYPE_ATTRIBUTE_TYPE_NONE = 0
TYPE_ATTRIBUTE_TYPE_VALUE_TABLE = 1
TYPE_ATTRIBUTE_TYPE_RATIONAL_SCALING = 2


class AttributeParser(BaseParser):
    """
    Parser for APX port and type attributes
    """

    def __init__(self) -> None:
        super().__init__()
        self.array_re = re.compile(r'\[\s*([1-9][0-9]*)\s*\]')
        self.state: AttributeParseState | None = None
        self.stack: list[AttributeParseState] = []

    def parse_port_attributes(
        self,
        attribute_string: str
    ) -> tuple[apx_base.Result, apx_model.PortAttributes | None]:
        """
        Parses a port attribute string (e.g. '=0', 'P', 'Q[10]')
        """
        self.reset(attribute_string)
        attr = apx_model.PortAttributes()
        result = apx_base.Result.NO_ERROR

        assert self.input is not None and self.read_position is not None
        while self.read_position < len(self.input):
            if self._lstrip():
                result = self._parse_single_port_attribute(attr)
            else:
                break
            if result == apx_base.Result.NO_ERROR:
                if self._lstrip():
                    c = self._read()
                    if c == ',':
                        self._move(1)
                    else:
                        return self._error(apx_base.Result.PARSE_ERROR), None
                else:
                    break
            else:
                return self._error(result), None
        if self.read_position != len(self.input):
            return self._error(apx_base.Result.STRAY_CHARACTERS_AFTER_PARSE_ERROR), None
        return result, attr

    def parse_type_attributes(
        self,
        attribute_string: str
    ) -> tuple[apx_base.Result, apx_model.TypeAttributes | None]:
        """
        Parses type attributes (e.g. 'VT(...)', 'RS(...)')
        """
        self.reset(attribute_string)
        attr = apx_model.TypeAttributes()
        result = apx_base.Result.NO_ERROR

        assert self.input is not None and self.read_position is not None
        while self.read_position < len(self.input):
            if self._lstrip():
                result = self._parse_single_type_attribute(attr)
            else:
                break
            if result == apx_base.Result.NO_ERROR:
                if self._lstrip():
                    c = self._read()
                    if c == ',':
                        self._move(1)
                    else:
                        return self._error(apx_base.Result.PARSE_ERROR), None
                else:
                    break
            else:
                return self._error(result), None
        if self.read_position != len(self.input):
            return self._error(apx_base.Result.STRAY_CHARACTERS_AFTER_PARSE_ERROR), None
        return result, attr

    def _parse_scalar(self) -> apx_base.Result:
        assert self.state is not None
        c = self._read()
        if c.isdigit():
            self.state.scalar_value = self._parse_integer()
            if self.state.scalar_value is None:
                return apx_base.Result.PARSE_ERROR
        elif c == '-':
            c = self._next()
            if c is None:
                return apx_base.Result.PARSE_ERROR
            self.state.scalar_value = self._parse_integer(True)
            if self.state.scalar_value is None:
                return apx_base.Result.PARSE_ERROR
        elif c == '"':
            result, self.state.scalar_value = self.parse_string_literal()
            if result != apx_base.Result.NO_ERROR:
                return result
        else:
            return apx_base.Result.NOT_IMPLEMENTED_ERROR
        return apx_base.Result.NO_ERROR

    @property
    def _is_initializer_list(self) -> bool:
        return bool(self.state is not None and self.state.parent is not None)

    def _parse_single_port_attribute(self, attr: apx_model.PortAttributes) -> apx_base.Result:
        self.state = AttributeParseState()
        c = self._next()
        if c == '=':
            result = self._parse_initializer(attr)
        elif c == 'P':
            attr.is_parameter = True
            result = apx_base.Result.NO_ERROR
        elif c == 'Q':
            result = self._parse_array_length(attr)
        else:
            result = apx_base.Result.PARSE_ERROR
        self.state = None
        return result

    def _parse_initializer(self, attr: apx_model.PortAttributes) -> apx_base.Result:
        assert self.state is not None
        result = self._parse_initializer_list()
        if result == apx_base.Result.NO_ERROR:
            if self.state.initializer_list is not None:
                attr.init_value = self.state.initializer_list
            elif self.state.scalar_value is not None:
                attr.init_value = self.state.scalar_value
            else:
                return apx_base.Result.NO_VALUE_ERROR
            return result
        else:
            return self._error(result)

    def _parse_array_length(self, attr: apx_model.PortAttributes) -> apx_base.Result:
        assert self.input is not None and self.read_position is not None
        tmp = self.input[self.read_position:]
        match = self.array_re.match(tmp)
        if match is not None:
            attr.queue_length = int(match.group(1))
            self.read_position += len(match.group(0))
            return apx_base.Result.NO_ERROR
        return apx_base.Result.PARSE_ERROR

    def _parse_initializer_list(self) -> apx_base.Result:
        assert self.input is not None and self.read_position is not None
        result = apx_base.Result.NO_ERROR
        while self.read_position < len(self.input):
            if self._lstrip():
                c = self._read()
                if c == '{':
                    self._next()
                    assert self.state is not None
                    self.state.initializer_list = []
                    self.stack.append(self.state)
                    child_state = AttributeParseState()
                    child_state.parent = self.state
                    self.state = child_state
                    continue
                if c != '}':
                    result = self._parse_scalar()
                    if result != apx_base.Result.NO_ERROR:
                        return result
                result, parsing_completed = self._post_value_handler()
                if result != apx_base.Result.NO_ERROR:
                    return result
                if parsing_completed:
                    break
        return result

    def _post_value_handler(self) -> tuple[apx_base.Result, bool]:
        parsing_completed = False
        if self._is_initializer_list:
            if self._lstrip():
                c = self._next()
                self._push_value_to_parent()
                assert self.state is not None and self.state.parent is not None
                is_not_empty = len(self.state.parent.initializer_list) > 0
                if is_not_empty and c == ',':
                    pass
                elif c == '}':
                    if len(self.stack) > 0:
                        self.state = self.stack.pop()
                        if len(self.stack) == 0:
                            parsing_completed = True
                        else:
                            # Recursively attempt to find closing braces until stack is empty
                            self._post_value_handler()
                    else:
                        raise RuntimeError("Parse stack unexpectedly empty")
                else:
                    self._move(-1)  # Unexpected character
                    return apx_base.Result.PARSE_ERROR, False
            else:
                return apx_base.Result.PARSE_ERROR, False
        else:
            parsing_completed = True
        return apx_base.Result.NO_ERROR, parsing_completed

    def _push_value_to_parent(self) -> None:
        assert self.state is not None and self.state.parent is not None
        if self.state.scalar_value is not None:
            self.state.parent.initializer_list.append(self.state.scalar_value)
            self.state.scalar_value = None
        elif self.state.initializer_list is not None:
            self.state.parent.initializer_list.append(self.state.initializer_list)
            self.state.initializer_list = None

    def _parse_single_type_attribute(self, attr: apx_model.TypeAttributes) -> apx_base.Result:
        assert self.input is not None and self.read_position is not None
        tmp = self.input[self.read_position:]
        if tmp.startswith('VT'):
            attr_type = TYPE_ATTRIBUTE_TYPE_VALUE_TABLE
        elif tmp.startswith('RS'):
            attr_type = TYPE_ATTRIBUTE_TYPE_RATIONAL_SCALING
        else:
            return apx_base.Result.PARSE_ERROR
        self.read_position += 2  # Consume the 'VT' or 'RS' string
        if self._lstrip():
            if attr_type == TYPE_ATTRIBUTE_TYPE_VALUE_TABLE:
                result, value_table = self._parse_value_table()
                if result == apx_base.Result.NO_ERROR and value_table is not None:
                    attr.computations.append(value_table)
            elif attr_type == TYPE_ATTRIBUTE_TYPE_RATIONAL_SCALING:
                result, rational_scaling = self._parse_rational_scaling()
                if result == apx_base.Result.NO_ERROR and rational_scaling is not None:
                    attr.computations.append(rational_scaling)
            else:
                return apx_base.Result.PARSE_ERROR
        else:
            return apx_base.Result.PARSE_ERROR
        return result

    def _parse_value_table(self) -> tuple[apx_base.Result, apx_model.ValueTable | None]:
        result = apx_base.Result.PARSE_ERROR
        if self._match_char('('):
            vt_state = ValueTableParseState()
            assert self.input is not None and self.read_position is not None
            while self.read_position < len(self.input):
                if self._lstrip():
                    result = self._parse_next_value_table_arg(vt_state)
                    if result != apx_base.Result.NO_ERROR:
                        break
                    if self._lstrip():
                        c = self._read()
                        if c is None:
                            break
                        elif c == ',':
                            self._move(1)
                        elif c == ')':
                            vt = self._create_value_table_from_parse_state(vt_state)
                            self._move(1)
                            return apx_base.Result.NO_ERROR, vt
                        else:
                            break
                    else:
                        break
                else:
                    break
        return result, None

    def _parse_rational_scaling(self) -> tuple[apx_base.Result, apx_model.RationalScaling | None]:
        result = apx_base.Result.PARSE_ERROR
        if self._match_char('('):
            rs_state = RationalScalingParseState()
            assert self.input is not None and self.read_position is not None
            while self.read_position < len(self.input):
                if self._lstrip():
                    result = self._parse_next_rational_scaling_arg(rs_state)
                    if result != apx_base.Result.NO_ERROR:
                        break
                    if self._lstrip():
                        c = self._read()
                        if c is None:
                            break
                        elif c == ',':
                            self._move(1)
                        elif c == ')':
                            rs = self._create_rational_scaling_from_parse_state(rs_state)
                            self._move(1)
                            return apx_base.Result.NO_ERROR, rs
                        else:
                            break
                    else:
                        break
                else:
                    break
        return result, None

    def _parse_next_value_table_arg(self, vt_state: ValueTableParseState) -> apx_base.Result:
        c = self._read()
        if c is None:
            return apx_base.Result.PARSE_ERROR
        unary_minus = False
        arg_type = VALUE_TABLE_ARG_TYPE_INVALID
        if vt_state.last_was_string:
            if c == '"':
                arg_type = VALUE_TABLE_ARG_TYPE_STRING_LITERAL
        else:
            if c == '"':
                arg_type = VALUE_TABLE_ARG_TYPE_STRING_LITERAL
            elif c == '-':
                unary_minus = True
                self._move(1)
                arg_type = VALUE_TABLE_ARG_TYPE_INTEGER
            elif self._is_digit(c):
                arg_type = VALUE_TABLE_ARG_TYPE_INTEGER
        if arg_type == VALUE_TABLE_ARG_TYPE_INVALID:
            return apx_base.Result.PARSE_ERROR
        if arg_type == VALUE_TABLE_ARG_TYPE_INTEGER:
            if vt_state.arg_pos == 0:
                result = self._parse_lower_limit(unary_minus, vt_state)
            elif vt_state.arg_pos == 1:
                result = self._parse_upper_limit(unary_minus, vt_state)
            else:
                result = apx_base.Result.PARSE_ERROR
            if result != apx_base.Result.NO_ERROR:
                return result
            vt_state.arg_pos += 1
            return apx_base.Result.NO_ERROR
        if arg_type == VALUE_TABLE_ARG_TYPE_STRING_LITERAL:
            vt_state.last_was_string = True
            result, value = self.parse_string_literal()
            if result != apx_base.Result.NO_ERROR:
                return result
            assert value is not None
            vt_state.values.append(str(value))
            return result
        return apx_base.Result.PARSE_ERROR

    def _create_value_table_from_parse_state(self, vt_state: ValueTableParseState) -> apx_model.ValueTable:
        vt = apx_model.ValueTable()
        auto_upper_limit = False
        if vt_state.arg_pos == 0:
            vt.lower_limit = 0
            vt.upper_limit = 0
            auto_upper_limit = True
        elif vt_state.arg_pos == 1:
            vt.lower_limit = vt_state.lower_limit
            vt.upper_limit = vt_state.lower_limit
            auto_upper_limit = True
        else:
            vt.lower_limit = vt_state.lower_limit
            vt.upper_limit = vt_state.upper_limit
        assert isinstance(vt.lower_limit, int)
        index = vt.lower_limit
        for text_value in vt_state.values:
            vt.append(text_value)
            if auto_upper_limit and (vt.upper_limit is None or vt.upper_limit < index):
                vt.upper_limit = index
            index += 1
        return vt

    def _parse_next_rational_scaling_arg(self, rs_state: RationalScalingParseState) -> apx_base.Result:
        unary_minus = False
        if rs_state.arg_pos == 0:
            if self._match_char('-'):
                unary_minus = True
            result = self._parse_lower_limit(unary_minus, rs_state)
        elif rs_state.arg_pos == 1:
            if self._match_char('-'):
                unary_minus = True
            result = self._parse_upper_limit(unary_minus, rs_state)
        elif rs_state.arg_pos == 2:
            result = self._parse_offset(rs_state)
        elif rs_state.arg_pos == 3:
            if self._match_char('-'):
                unary_minus = True
            result = self._parse_numerator(rs_state)
        elif rs_state.arg_pos == 4:
            if self._match_char('-'):
                unary_minus = True
            result = self._parse_denominator(rs_state)
        elif rs_state.arg_pos == 5:
            result = self._parse_unit(rs_state)
        else:
            result = apx_base.Result.PARSE_ERROR
        if result == apx_base.Result.NO_ERROR:
            rs_state.arg_pos += 1
        return result

    def _create_rational_scaling_from_parse_state(
        self,
        state: RationalScalingParseState
    ) -> apx_model.RationalScaling:
        rs = apx_model.RationalScaling()
        rs.lower_limit = state.lower_limit
        rs.upper_limit = state.upper_limit
        rs.offset = state.offset
        rs.numerator = state.numerator
        rs.denominator = state.denominator
        rs.unit = state.unit
        return rs

    def _parse_lower_limit(self, unary_minus: bool, parse_state: ComputationParseState) -> apx_base.Result:
        value = self._parse_integer(unary_minus)
        if value is None:
            return apx_base.Result.PARSE_ERROR
        parse_state.lower_limit = value
        return apx_base.Result.NO_ERROR

    def _parse_upper_limit(self, unary_minus: bool, parse_state: ComputationParseState) -> apx_base.Result:
        value = self._parse_integer(unary_minus)
        if value is None:
            return apx_base.Result.PARSE_ERROR
        parse_state.upper_limit = value
        return apx_base.Result.NO_ERROR

    def _parse_offset(self, parse_state: RationalScalingParseState) -> apx_base.Result:
        value = self._parse_float()
        if value is None:
            return apx_base.Result.PARSE_ERROR
        parse_state.offset = value
        return apx_base.Result.NO_ERROR

    def _parse_numerator(self, parse_state: RationalScalingParseState) -> apx_base.Result:
        unary_minus = False
        if self._match_char('-'):
            unary_minus = True
        value = self._parse_integer(unary_minus)
        if value is None:
            return apx_base.Result.PARSE_ERROR
        parse_state.numerator = value
        return apx_base.Result.NO_ERROR

    def _parse_denominator(self, parse_state: RationalScalingParseState) -> apx_base.Result:
        unary_minus = False
        if self._match_char('-'):
            unary_minus = True
        value = self._parse_integer(unary_minus)
        if value is None:
            return apx_base.Result.PARSE_ERROR
        parse_state.denominator = value
        return apx_base.Result.NO_ERROR

    def _parse_unit(self, parse_state: RationalScalingParseState) -> apx_base.Result:
        result, value = self.parse_string_literal()
        if result == apx_base.Result.NO_ERROR:
            parse_state.unit = value
        return result
