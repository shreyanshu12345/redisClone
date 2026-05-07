from hashlib import sha256

def write_length(f, length):
    if length < 64:
        f.write(bytes([length]))
    else:
        raise ValueError("Length encoding > 63 not implemented.")

def write_string(f, s):
    encoded = s.encode('utf-8')
    write_length(f, len(encoded))
    f.write(encoded)

def write_rdb_string_key(f, key, value):
    f.write(bytes([0x00]))
    write_string(f, key)
    write_string(f, value)

def write_rdb_file(data_dict, filename='dump.rdb'):
    with open(filename, 'wb') as f:
        f.write(b'REDIS0009')
        f.write(bytes([0xFE, 0x00]))
        for k, v in data_dict.items():
            write_rdb_string_key(f, k, v)
        f.write(bytes([0xFF]))

    with open(filename, "r+b") as f:
        info = f.read()
        hash = sha256(info).digest()
        f.write(hash)