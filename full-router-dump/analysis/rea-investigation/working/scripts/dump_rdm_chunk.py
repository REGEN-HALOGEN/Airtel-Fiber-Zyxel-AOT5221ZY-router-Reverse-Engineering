with open('files/config_rdm_decompressed.bin', 'rb') as f:
    data = f.read()

def dump_region(start, length):
    print(f"=== Region {hex(start)} to {hex(start+length)} ===")
    chunk = data[start:start+length]
    for i in range(0, length, 16):
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk[i:i+16])
        print(f"  {hex(start+i)}: {hex_bytes:<48} | {ascii_str}")

dump_region(0x36e70, 0x200)
dump_region(0x3b2b0, 0x150)

