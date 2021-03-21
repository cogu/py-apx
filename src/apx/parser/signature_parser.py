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
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #{. TODO: Perhaps introduce TOKEN_CLASS_RECORD?
    apx.base.TOKEN_GROUP_DECLARATION,      #[
    apx.base.TOKEN_FUNCTION_DECLARATION,   #(
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #T
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #a
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #A
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #b
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #B
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #c
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #C
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #l
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #L
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #q
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #Q
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #s
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #S
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #u
    apx.base.TOKEN_CLASS_DATA_ELEMENT,     #U
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

class SignatureParser:
    def parse_signature(self, signature):
        remain = signature
        c=remain[0]        
        try:
            i = TYPE_CODE_CHAR_MAP.index(c)
            remain = remain[1:]
        except ValueError:
            return (None,remain)
        token_class = TOKEN_CLASS_MAP[i]
        type_code = TYPE_CODE_MAP[i]
        is_signed_type = SIGNED_TYPE_MAP[i]
        is_64_bit_type = True if (type_code == apx.base.TYPE_CODE_INT64 or type_code == apx.base.TYPE_CODE_UINT64) else False
        check_limits = False
        data_element = apx.data_element.DataElement(type_code)
        return data_element, remain