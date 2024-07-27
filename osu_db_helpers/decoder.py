
import os
import struct

def decode_byte(fp) -> int:
    return struct.unpack('<B', fp.read(0x01))[0]

def decode_int(fp) -> int:
    return struct.unpack('<I', fp.read(0x04))[0]

def decode_float(fp) -> float:
    return struct.unpack('<f', fp.read(0x04))[0]

def decode_uleb128(fp) -> int:
    a = bytearray()
    while True:
        b = ord(fp.read(0x01))
        a.append(b)
        if (b & 0x80) == 0:
            break
    r = 0
    for i, e in enumerate(a):
        r = r + ((e & 0x7f) << (i * 7))
    return r

def decode_ulebstring(fp) -> str:
    if decode_byte(fp) == 0:
        return ""
    length = decode_uleb128(fp)
    data = struct.unpack(f'<{length}s', fp.read(length))
    return data[0].decode('utf-8')

def seek_ulebstring(fp) -> None:
    if decode_byte(fp) == 0:
        return
    length = decode_uleb128(fp)
    fp.seek(length, os.SEEK_CUR)

def encode_int(value, fp) -> None:
    r = struct.pack('<I', value)
    fp.write(r)

def encode_long(value, fp) -> None:
    r = struct.pack('<Q', value)
    fp.write(r)

def encode_double(value, fp) -> None:
    r = struct.pack('<d', value)
    fp.write(r)
