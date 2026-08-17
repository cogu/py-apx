"""
Base parser and text-splitting utilities for APX
"""
import io
import re
import apx.base as apx_base

type_declaration_line_re = re.compile(r'T"(\w+)"(.+?):(.+)|T"(\w+)"([^:]+)')
port_declaration_line_re = re.compile(r'([PR])"(\w+)"(.+?):(.+)|([PR])"(\w+)"([^:]+)')
line_comment_re = re.compile(r'#(.*)')


def strip_comment(apx_text: str) -> str:
    """
    Strips comments starting with # from APX text
    """
    return re.sub(line_comment_re, '', apx_text)


def split_type_declaration(apx_text: str) -> tuple[str, str, str | None] | None:
    """
    Splits a type declaration line into tokens.
    Returns a 3-element tuple:
        1. Type Name : str
        2. Type Signature : str
        3. Type Attribute : str | None
    """
    match = type_declaration_line_re.match(apx_text)
    if match is not None:
        if match.group(1) is not None:
            return match.group(1), match.group(2), match.group(3)
        else:
            return match.group(4), match.group(5), None
    return None


def split_port_declaration(apx_text: str) -> tuple[str, str, str, str | None] | None:
    """
    Splits a port declaration line into tokens.
    Returns a 4-element tuple:
        1. Port Type : str ('P' or 'R')
        2. Type Name : str
        3. Type Signature : str
        4. Type Attribute : str | None
    """
    match = port_declaration_line_re.match(apx_text)
    if match is not None:
        if match.group(1) is not None:
            return match.group(1), match.group(2), match.group(3), match.group(4)
        else:
            return match.group(5), match.group(6), match.group(7), None
    return None


class BaseParser:
    """
    Low-level scanner and parser base class
    """

    def __init__(self) -> None:
        self.last_error: apx_base.Result = apx_base.Result.NO_ERROR
        self.digit_re = re.compile(r'[0-9]')
        self.int_re = re.compile(r'0x([1-9a-fA-F][0-9a-fA-F]*)|(-?[1-9][0-9]*)|0x(0+)|(0+)')
        self.float_re = re.compile(r'[+-]?([0-9]*[.])?[0-9]+')
        self.ws_re = re.compile(r'[\t\n\r ]+')
        self.input: str | None = None
        self.ch: str | None = None
        self.read_position: int | None = None

    def reset(self, text: str) -> None:
        """
        Resets parser state with new input text
        """
        self.last_error = apx_base.Result.NO_ERROR
        self.input = text
        self.read_position = 0
        self.ch = None

    def is_input_consumed(self) -> bool:
        """
        Returns True if read_position points to one character after length of input string
        """
        if isinstance(self.read_position, int) and isinstance(self.input, str):
            return self.read_position == len(self.input)
        return False

    def _next(self) -> str | None:
        """
        Moves read position forward by 1 character. Returns the read character.
        """
        assert (self.input is not None) and (self.read_position is not None)
        if self.read_position < len(self.input):
            self.ch = self.input[self.read_position]
            self.read_position += 1
        else:
            self.ch = None
        return self.ch

    def _move(self, amount: int) -> None:
        """
        Moves read position the given amount
        """
        assert (self.input is not None) and (self.read_position is not None)
        self.read_position += int(amount)

    def _read(self) -> str:
        """
        Returns character at current read position
        """
        assert (self.input is not None) and (self.read_position is not None)
        return self.input[self.read_position]

    def _match_char(self, expect_char: str) -> bool:
        """
        Moves read position forward by 1 only if the input matches expected character.
        Returns True if input matches, False otherwise.
        """
        assert (self.input is not None) and (self.read_position is not None)
        if self.read_position < len(self.input):
            if self.input[self.read_position] == expect_char:
                self.ch = self.input[self.read_position]
                self.read_position += 1
                return True
        else:
            self.ch = None
        return False

    def _test_char(self, expect_char: str) -> bool:
        """
        Test if next character matches expected input but does not move read position forward
        """
        assert (self.input is not None) and (self.read_position is not None)
        if self.read_position < len(self.input) and self.input[self.read_position] == expect_char:
            return True
        return False

    def _lstrip(self) -> bool:
        """
        Skips whitespace.
        Returns True if there are more characters to parse after whitespace.
        """
        assert (self.input is not None) and (self.read_position is not None)
        match = self.ws_re.match(self.input[self.read_position:])
        if match is not None:
            self.read_position += len(match.group())
        if self.read_position < len(self.input):
            self.ch = self.input[self.read_position]
            return True
        return False

    def _error(self, error_code: apx_base.Result) -> apx_base.Result:
        """
        Sets the error code for later retrieval
        """
        self.last_error = error_code
        return error_code

    def _is_digit(self, c: str) -> bool:
        return self.digit_re.match(c) is not None

    def parse_uint64(self) -> int | None:
        """
        Parses an unsigned 64-bit integer literal
        """
        return self._parse_uint(64)

    def parse_uint32(self) -> int | None:
        """
        Parses an unsigned 32-bit integer literal
        """
        return self._parse_uint(32)

    def parse_uint16(self) -> int | None:
        """
        Parses an unsigned 16-bit integer literal
        """
        return self._parse_uint(16)

    def parse_uint8(self) -> int | None:
        """
        Parses an unsigned 8-bit integer literal
        """
        return self._parse_uint(8)

    def _parse_uint(self, bits: int) -> int | None:
        """
        Helper function for uint parsing
        """
        assert self.read_position is not None
        current_position = self.read_position
        result = self._parse_integer()
        if result is not None:
            if result < 0 or result.bit_length() > bits:
                self.read_position = current_position
                return None
        return result

    def parse_int8(self) -> int | None:
        """
        Parses a signed 8-bit integer literal
        """
        return self._parse_int(8)

    def parse_int16(self) -> int | None:
        """
        Parses a signed 16-bit integer literal
        """
        return self._parse_int(16)

    def parse_int32(self) -> int | None:
        """
        Parses a signed 32-bit integer literal
        """
        return self._parse_int(32)

    def parse_int64(self) -> int | None:
        """
        Parses a signed 64-bit integer literal
        """
        return self._parse_int(64)

    def _parse_int(self, bits: int) -> int | None:
        """
        Helper function for int parsing
        """
        assert self.read_position is not None
        current_position = self.read_position
        result = self._parse_integer()
        lower_limit = -2**(bits - 1)
        upper_limit = 2**(bits - 1) - 1
        if result is not None:
            if result < lower_limit or result > upper_limit:
                self.read_position = current_position
                return None
        return result

    def _parse_integer(self, unary_minus: bool = False) -> int | None:
        """
        On Success: Returns integer
        On Failure: Returns None
        """
        assert (self.input is not None) and (self.read_position is not None)
        tmp = self.input[self.read_position:]
        match = self.int_re.match(tmp)
        if match is not None:
            next_position = self.read_position
            if match.group(1) is not None:
                tmp = match.group(1)
                result = int(tmp, 16)
                next_position += 2  # Add 2 for the '0x' prefix
            elif match.group(2) is not None:
                tmp = match.group(2)
                result = int(tmp, 10)
            elif match.group(3) is not None:
                tmp = match.group(3)
                next_position += 2
                result = 0
            elif match.group(4) is not None:
                tmp = match.group(4)
                result = 0
            else:
                raise RuntimeError()
            self.read_position = next_position + len(tmp)
            return -result if unary_minus else result
        return None

    def _parse_float(self) -> float | None:
        """
        On Success: Returns float
        On Failure: Returns None
        """
        assert (self.input is not None) and (self.read_position is not None)
        tmp = self.input[self.read_position:]
        match = self.float_re.match(tmp)
        if match is not None:
            tmp = match.group(0)
            value = float(tmp)
            self.read_position = self.read_position + len(tmp)
            return value
        return None

    def parse_string_literal(self) -> tuple[apx_base.Result, str | None]:
        """
        Returns error code and parsed literal
        """
        assert self.read_position is not None
        if self._test_char('"'):
            self.read_position += 1
            is_escaped = False
            literal = io.StringIO()
            while True:
                c = self._next()
                if c is None:
                    return apx_base.Result.UNMATCHED_STRING_ERROR, None
                if is_escaped:
                    is_escaped = False
                    if c == '"':
                        literal.write(c)
                    else:
                        # Other escaped characters not yet supported
                        return apx_base.Result.NOT_IMPLEMENTED_ERROR, None
                else:
                    if c == '"':
                        break
                    if c == '\\':
                        is_escaped = True
                    else:
                        literal.write(c)
            return apx_base.Result.NO_ERROR, literal.getvalue()
        return apx_base.Result.PARSE_ERROR, None
