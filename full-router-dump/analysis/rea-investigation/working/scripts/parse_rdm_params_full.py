import struct

with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

# Let's inspect bytes from 0x3b344
# Each parameter descriptor starts with length byte
pos = 0x3b344
params = []

for idx in range(120): # up to 120 parameters
    if pos >= len(data): break
    length = data[pos]
    if length == 0 or length > 120:
        break
    entry_bytes = data[pos:pos+length]
    # Name starts at pos+1
    name_bytes = entry_bytes[1:]
    null_idx = name_bytes.find(b'\x00')
    name = name_bytes[:null_idx].decode('latin1', errors='ignore') if null_idx != -1 else ""
    
    # Let's unpack the rest of entry_bytes
    # Look at the end of the entry:
    # In 0x3b344, length was 0x34 (52)
    # entry_bytes has length 52
    # At +0x28 (or 40): d4 09 00 00 00 00 00 00 -> 0x9d4
    # Let's print all fields
    params.append((pos, length, name, entry_bytes))
    pos += length

print(f"Parsed {len(params)} parameters under WANPPPConnection:")
for p, l, name, b in params:
    # Print trailing 24 bytes in hex and uint32s
    tail = b[len(name)+2:]
    # look for offsets (usually uint32/uint64)
    uints = [struct.unpack('<I', b[i:i+4])[0] for i in range(len(b)-16, len(b), 4)]
    print(f"  [0x{p:05x}] len=0x{l:02x} | {name:32s} | tail: {tail.hex(' ')}")


