def _decode(data, mode=16, offset=0, end=None):
    """
    Decodes numheader from data (which is byte or bytearray).
    Mode can be either 16 or 32 (number of bits parsed when long_bit is 1)

    Returns tuple (bytesParsed, value)
    """
    bytesParsed = 0
    value = None
    if end is None:
        end = len(data)
    if offset+1 <= end:  # at least 1 byte in data?
        b1 = data[offset]
        if b1 & 0x80:
            b1 &= 0x7F
            # MSB is set, parse next 1 or 3 bytes depending on mode
            if mode == 16:  # NumHeader16
                if offset+2 <= end:
                    bytesParsed = 2
                    b2 = data[offset+1]
                    value = (b1 << 8 | b2)
                    # range(0,128) with MSB set to 1 shall be interpreted as 32768..32895
                    if value < 128:
                        value += 32768
            elif mode == 32:  # NumHeader32
                if offset+4 <= end:
                    bytesParsed = 4
                    b2, b3, b4 = data[offset+1:offset+4]
                    value = (b1 << 24) | (b2 << 16) | (b3 << 8) | b4
            else:
                raise ValueError('invalid mode argument: '+str(mode))
        else:
            bytesParsed = 1
            value = b1
    return (bytesParsed, value)


def decode16(data, offset=0, end=None):
    """
    Decodes NumHeader16 value from bytearray

    Returns tuple (bytesParsed, value)
    """
    return _decode(data, 16, offset, end)


def decode32(data, offset=0, end=None):
    """
    Decodes NumHeader32 value from bytearray

    Returns tuple (bytesParsed, value)
    """
    return _decode(data, 32, offset, end)


def _encode(value, mode):
    """
    Mode can be either 16 or 32 (number of bits written when long_bit is 1)

    returns a bytes object
    """
    if value < 128:
        return bytes([value])
    else:
        if mode == 16:
            if value < 32768:
                return bytes([0x80 | (value >> 8), value & 0xFF])
            elif value < 32896:
                return bytes([0x80, (value-32768) & 0xFF])
            else:
                raise ValueError("value must be an integer in range(0,32896)")
        elif mode == 32:
            if value < 2147483648:
                return bytes([(0x80 | ((value >> 24) & 0xFF)), (value >> 16) & 0xFF, (value >> 8) & 0xFF, (value & 0xFF)])
            else:
                raise ValueError(
                    "value must be an integer in range(0,2147483648)")
        else:
            raise ValueError('invalid mode argument: '+str(mode))


def encode16(value):
    """
    Encodes NumHeader16 value

    returns bytes object
    """
    return _encode(value, 16)


def encode32(value):
    """
    Encodes NumHeader32 value

    returns bytes object
    """
    return _encode(value, 32)
