with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

for off_target, label in [(0x3c011, "0x3e7 target"), (0x3c7b4, "0x898 target")]:
    print(f"\n==================== {label} around 0x{off_target:x} ====================")
    chunk = data[off_target-32:off_target+96]
    print("Hex dump:")
    for i in range(0, len(chunk), 16):
        print(f"  +0x{i:02x}: {chunk[i:i+16].hex(' ')} | {bytes(b if 32 <= b < 127 else 46 for b in chunk[i:i+16]).decode('latin1')}")


