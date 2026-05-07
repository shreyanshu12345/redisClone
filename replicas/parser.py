from hashlib import sha256


def read_length(f):
    b = f.read(1)
    if not b:
        raise EOFError("Unexpected end of file when reading length.")
    return b[0]

def read_string(f):
    length = read_length(f)
    return f.read(length).decode('utf-8')

def parse_rdb_file(filename):
    
    with open(filename, 'rb') as f:
        header = f.read(9)
        if header != b'REDIS0009':
            raise ValueError("Invalid header")

        if f.read(2) != b'\xFE\x00':
            raise ValueError("Missing DB selector")

        data = {}
        while True:
            b = f.read(1)
            if not b:
                break
            if b == b'\xFF':
                break
            if b != b'\x00':
                raise ValueError("Unsupported type: " + b.hex())
            key = read_string(f)
            value = read_string(f)
            data[key] = value

        file_hash = f.read(32)
        expected_hash = sha256(open(filename, 'rb').read()[:-32]).digest()
        if file_hash != expected_hash:
            raise ValueError("Hash mismatch")

        return data




