"""Functions for encoding and decoding APX numeric headers.

NumHeader encodes an integer in Big-Endian (network byte order),
commonly used as a message length prefix. The most significant bit
(MSB / bit 7) of the first byte acts as a `LONG_BIT`:
- `0`: 1-byte short form (values 0..127)
- `1`: Multi-byte long form (2 bytes for NumHeader16, 4 bytes for NumHeader32)
"""
import struct

_ST_UINT16 = struct.Struct('>H')
_ST_UINT32 = struct.Struct('>I')


def decode16(data: bytes | bytearray, offset: int = 0,
             end: int | None = None) -> tuple[int, int | None]:
    """Decodes a NumHeader16 value from a byte buffer.

    NumHeader16 parses 1 byte for values 0..127 and 2 bytes for
    values 128..32,895.

    Args:
        data: Byte buffer containing encoded NumHeader16 data.
        offset: Starting byte index in buffer (defaults to 0).
        end: Ending byte index in buffer (defaults to len(data)).

    Returns:
        A tuple of `(bytes_parsed, value)`:
        - `bytes_parsed`: Number of bytes consumed (1, 2, or 0 if short).
        - `value`: Decoded integer (0..32,895), or `None` if buffer is short.
    """
    if end is None:
        end = len(data)
    if offset + 1 <= end:
        if (data[offset] & 0x80) == 0:
            return 1, data[offset]
        if offset + 2 <= end:
            val = _ST_UINT16.unpack_from(data, offset)[0] & 0x7FFF
            if val < 128:
                val += 32768
            return 2, val
    return 0, None


def decode32(data: bytes | bytearray, offset: int = 0,
             end: int | None = None) -> tuple[int, int | None]:
    """Decodes a NumHeader32 value from a byte buffer.

    NumHeader32 parses 1 byte for values 0..127 and 4 bytes for
    values 128..2,147,483,647.

    Args:
        data: Byte buffer containing encoded NumHeader32 data.
        offset: Starting byte index in buffer (defaults to 0).
        end: Ending byte index in buffer (defaults to len(data)).

    Returns:
        A tuple of `(bytes_parsed, value)`:
        - `bytes_parsed`: Number of bytes consumed (1, 4, or 0 if short).
        - `value`: Decoded integer (0..2,147,483,647), or `None` if short.
    """
    if end is None:
        end = len(data)
    if offset + 1 <= end:
        if (data[offset] & 0x80) == 0:
            return 1, data[offset]
        if offset + 4 <= end:
            val = _ST_UINT32.unpack_from(data, offset)[0] & 0x7FFFFFFF
            return 4, val
    return 0, None


def encode16(value: int) -> bytes:
    """Encodes an integer as a NumHeader16 value.

    Encodes values in the range 0..32,895 using either 1 byte (0..127)
    or 2 bytes (128..32,895).

    Args:
        value: Non-negative integer to encode (0 <= value <= 32,895).

    Returns:
        A `bytes` object of length 1 (value < 128) or 2 (value >= 128).

    Raises:
        ValueError: If `value` is negative or greater than 32,895.
    """
    if 0 <= value < 128:
        return bytes([value])
    if 128 <= value < 32768:
        return _ST_UINT16.pack(0x8000 | value)
    if 32768 <= value < 32896:
        return _ST_UINT16.pack(0x8000 | (value - 32768))
    raise ValueError("value must be an integer in range(0,32896)")


def encode32(value: int) -> bytes:
    """Encodes an integer as a NumHeader32 value.

    Encodes values in the range 0..2,147,483,647 using either 1 byte (0..127)
    or 4 bytes (128..2,147,483,647).

    Args:
        value: Non-negative integer to encode (0 <= value <= 2,147,483,647).

    Returns:
        A `bytes` object of length 1 (value < 128) or 4 (value >= 128).

    Raises:
        ValueError: If `value` is negative or greater than 2,147,483,647.
    """
    if 0 <= value < 128:
        return bytes([value])
    if 128 <= value < 2147483648:
        return _ST_UINT32.pack(0x80000000 | value)
    raise ValueError("value must be an integer in range(0,2147483648)")
