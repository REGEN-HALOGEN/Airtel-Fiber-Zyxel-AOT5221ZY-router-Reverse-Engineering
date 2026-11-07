with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

for p in [0x3b2f0, 0x3b344, 0x3b2dc]:
    print(f"\n--- At 0x{p:x} ---")
    chunk = data[p:p+48]
    print(chunk.hex(' '))
    print(bytes(b if 32 <= b < 127 else 46 for b in chunk).decode('latin1'))


