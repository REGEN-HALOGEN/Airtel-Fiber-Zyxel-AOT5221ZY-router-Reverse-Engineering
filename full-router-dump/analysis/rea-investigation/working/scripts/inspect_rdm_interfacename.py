with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

pos = 0
while True:
    idx = data.find(b'X_5067F0_InterfaceName', pos)
    if idx == -1: break
    print(f"Found 'X_5067F0_InterfaceName' at offset 0x{idx:x}")
    # Inspect 64 bytes before and after
    start = max(0, idx - 32)
    end = min(len(data), idx + 64)
    print(f"  Hex before: {data[start:idx].hex(' ')}")
    print(f"  Hex after:  {data[idx:end].hex(' ')}")
    pos = idx + len(b'X_5067F0_InterfaceName')


