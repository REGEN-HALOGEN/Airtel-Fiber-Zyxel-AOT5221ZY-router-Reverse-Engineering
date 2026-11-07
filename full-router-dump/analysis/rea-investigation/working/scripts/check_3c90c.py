with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

off = 0x3c90c
chunk = data[off-16:off+64]
print(f"Around 0x{off:x} in config_rdm_decompressed.bin:")
for i in range(0, len(chunk), 16):
    print(f"  +0x{i:02x}: {chunk[i:i+16].hex(' ')} | {bytes(b if 32 <= b < 127 else 46 for b in chunk[i:i+16]).decode('latin1')}")


