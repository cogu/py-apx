import re
import apx.base
import apx.data_element

TYPE_CODE_CHAR_MAP=[
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

TOKEN_CLASS_MAP = [
    apx.base.TOKEN_CLASS_RECORD_DECLARATION,     #{
    apx.base.TOKEN_CLASS_GROUP_DECLARATION,      #[
    apx.base.TOKEN_CLASS_FUNCTION_DECLARATION,   #(
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #T
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #a
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #A
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #b
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #B
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #c
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #C
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #l
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #L
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #q
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #Q
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #s
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #S
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #u
    apx.base.TOKEN_CLASS_DATA_ELEMENT,           #U
]

TYPE_CODE_MAP = [
    apx.base.TYPE_CODE_NONE,      #{
    apx.base.TYPE_CODE_NONE,      #[
    apx.base.TYPE_CODE_NONE,      #(
    apx.base.TYPE_CODE_REF_ID,    #T. initial guess, refine later
    apx.base.TYPE_CODE_CHAR,      #a
    apx.base.TYPE_CODE_CHAR8,     #A
    apx.base.TYPE_CODE_BOOL,      #b
    apx.base.TYPE_CODE_BYTE,      #B
    apx.base.TYPE_CODE_INT8,      #c
    apx.base.TYPE_CODE_UINT8,     #C
    apx.base.TYPE_CODE_INT32,     #l
    apx.base.TYPE_CODE_UINT32,    #L
    apx.base.TYPE_CODE_INT64,     #q
    apx.base.TYPE_CODE_UINT64,    #Q
    apx.base.TYPE_CODE_INT16,     #s
    apx.base.TYPE_CODE_UINT16,    #S
    apx.base.TYPE_CODE_CHAR16,    #u
    apx.base.TYPE_CODE_CHAR32,    #U
]

SIGNED_TYPE_MAP = [
    False,                        #{
    False,                        #[
    False,                        #(
    False,                        #T. initial guess, refine later
    True,                         #a
    False,                        #A
    False,                        #b
    False,                        #B
    True,                         #c
    False,                        #C
    True,                         #l
    False,                        #L
    True,                         #q
    False,                        #Q
    True,                         #s
    False,                        #S
    False,                        #u
    False,                        #U
]

CHECK_LIMITS = [
    False,                        #{
    False,                        #[
    False,                        #(
    False,                        #T
    False,                        #a
    False,                        #A
    False,                        #b
    True,                         #B
    True,                         #c
    True,                         #C
    True,                         #l
    True,                         #L
    True,                         #q
    True,                         #Q
    True,                         #s
    True,                         #S
    False,                        #u
    False,                        #U
]

class State:
    def __init__(self, is_record = False):
        self.is_record = is_record
        self.data_element = None


class SignatureParser:

    def __init__(self):
        self.last_error = apx.base.NO_ERROR
        self.signature = None
        self.pos = None
        self.state = None
        self.int_re = re.compile('0x(0+)|(0+)|0x([1-9][0-9]*)|(-?[1-9][0-9]*)')
        self.ws_re = re.compile('[\t\n\r ]+')
        self.array_re = re.compile('\[([1-9][0-9]*)\]')

    def reset(self, signature):
        self.signature = signature
        self.pos = 0

    def parse_signature(self, signature):
        self.reset(signature)
        self.state = State()
        result = self.parse_data_element()
        if result == apx.base.NO_ERROR:
            if self.pos != len(self.signature):
                return self._error(apx.base.STRAY_CHARACTERS_AFTER_PARSE_ERROR)
            return self.state.data_element, result
        else:
            return self._error(result)

    def parse_data_element(self):
        c = self._next()
        try:
            i = TYPE_CODE_CHAR_MAP.index(c)
        except ValueError:
            self.pos-=1
            return apx.base.APX_PARSE_ERROR
        token_class = TOKEN_CLASS_MAP[i]
        type_code = TYPE_CODE_MAP[i]
        is_signed_type = SIGNED_TYPE_MAP[i]
        is_64_bit_type = True if (type_code == apx.base.TYPE_CODE_INT64 or type_code == apx.base.TYPE_CODE_UINT64) else False
        check_limits = CHECK_LIMITS[i]
        if token_class == apx.base.TOKEN_CLASS_RECORD_DECLARATION:
            self.state.data_element = apx.data_element.DataElement(type_code)
            raise NotImplementedError(token_class)
        elif token_class == apx.base.TOKEN_CLASS_DATA_ELEMENT:
            assert type_code != apx.base.TYPE_CODE_NONE
            self.state.data_element = apx.data_element.DataElement(type_code)
            if check_limits:
                if is_64_bit_type:
                    result = self._parse_limits_i64() if is_signed_type else self._parse_limits_u64()
                else:
                    result = self._parse_limits_i32() if is_signed_type else self._parse_limits_u32()
                if result != apx.base.NO_ERROR:
                    return result
            result = self._parse_array()
            if result != apx.base.NO_ERROR:
                return result
        else:
            raise NotImplementedError(token_class)
        return apx.base.NO_ERROR

    def _next(self):
        assert (self.signature is not None) and (self.pos is not None)
        if self.pos < len(self.signature):
            retval = self.signature[self.pos]
            self.pos+=1
            return retval
        return None

    def _match_char(self, c):
        assert (self.signature is not None) and (self.pos is not None)
        if self.pos < len(self.signature):
            if self.signature[self.pos] == c:
                self.pos+=1
                return True
        return False

    def _test_char(self, c):
        assert (self.signature is not None) and (self.pos is not None)
        if self.pos < len(self.signature):
            if self.signature[self.pos] == c:
                return True
        return False

    def _lstrip(self):
        assert (self.signature is not None) and (self.pos is not None)
        match = self.ws_re.match(self.signature[self.pos:])
        if match is not None:
            self.pos += len(match.group())
        return True if self.pos < len(self.signature) else False

    def _error(self, error_code):
        self.last_error = error_code
        return None, error_code

    def _parse_limits_i64(self):
        raise NotImplementedError()

    def _parse_limits_u64(self):
        raise NotImplementedError()

    def _parse_limits_u32(self):
        if self._test_char('('):
            self.pos += 1
            if self._lstrip():
                lower_limit = self._parse_u32()
                if lower_limit is None:
                    return apx.base.PARSE_ERROR
                if self._lstrip():
                    if self._match_char(','):
                        if self._lstrip():
                            upper_limit = self._parse_u32()
                            if upper_limit is None:
                                return apx.base.PARSE_ERROR
                            if self._lstrip():
                                if self._match_char(')'):
                                    self.state.data_element.set_limits(lower_limit, upper_limit)
                            return apx.base.NO_ERROR
            return apx.base.PARSE_ERROR
        return apx.base.NO_ERROR

    def _parse_limits_i32(self):
        raise NotImplementedError()

    def _parse_array(self):
        if self.pos < len(self.signature):
            tmp = self.signature[self.pos:]
            match = self.array_re.match(tmp)
            if match is not None:
                self.state.data_element.array_len = int(match.group(1))
                self.pos += len(match.group(0))
                return apx.base.NO_ERROR
            return apx.base.PARSE_ERROR
        return apx.base.NO_ERROR

    def _parse_u32(self):
        result = self._parse_integer()
        if result is not None:
            if result<0 or result.bit_length() > 32:
                return None
        return result

    def _parse_integer(self):
        tmp = self.signature[self.pos:]
        match = self.int_re.match(tmp)
        if match is not None:
            if match.group(1) is not None:
                tmp = match.group(1)
                result = 0
            elif match.group(2) is not None:
                tmp = match.group(2)
                result = 0
            elif match.group(3) is not None:
                tmp = match.group(3, 16)
            elif match.group(4) is not None:
                tmp = match.group(4)
                result = int(tmp, 10)
            else:
                raise RuntimeError()
            print(tmp)
            self.pos+=len(tmp)
            return result
        return None
