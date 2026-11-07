from elftools.elf.elffile import ELFFile
import struct

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_data = rodata.data()
    ro_addr = rodata['sh_addr']
    
    symtab = elf.get_section_by_name('.dynsym')
    oid_sym = None
    for sym in symtab.iter_symbols():
        if sym.name == 'OIDTable':
            oid_sym = sym
            break
            
    print(f"OIDTable: addr=0x{oid_sym['st_value']:x}, size={oid_sym['st_size']}")
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= oid_sym['st_value'] < s['sh_addr'] + s['sh_size']:
            sec = s
            break
            
    data = sec.data()
    offset = oid_sym['st_value'] - sec['sh_addr']
    table_bytes = data[offset:offset+oid_sym['st_size']]

# In MSTC librdm.so, what is each entry in OIDTable?
# Let's inspect the first few entries
print("First few entries (hex):")
for i in range(0, min(len(table_bytes), 256), 16):
    print(f"  +0x{i:03x}: {table_bytes[i:i+16].hex(' ')}")

# Let's search for 0x000000e3 (227) in table_bytes
pos = 0
while True:
    idx = table_bytes.find(b'\xe3\x00\x00\x00', pos)
    if idx == -1:
        break
    print(f"\nFound 0xe3 at offset 0x{idx:x} in OIDTable")
    # print surrounding 64 bytes
    start = max(0, idx - 16)
    end = min(len(table_bytes), idx + 48)
    # unpack pointers
    print(f"Bytes: {table_bytes[start:end].hex(' ')}")
    # If there are pointers into rodata, print string
    for off in range(start, end - 8, 8):
        ptr = struct.unpack('<Q', table_bytes[off:off+8])[0]
        if ro_addr <= ptr < ro_addr + len(ro_data):
            s_off = ptr - ro_addr
            s_end = ro_data.find(b'\x00', s_off)
            print(f"  Ptr at table+0x{off:x} -> 0x{ptr:x}: {ro_data[s_off:s_end].decode('latin1', errors='replace')}")
    pos = idx + 4


