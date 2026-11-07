from elftools.elf.elffile import ELFFile
import struct

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= 0x294f0 < s['sh_addr'] + s['sh_size']:
            sec = s
            break
            
    data = sec.data()
    offset = 0x294f0 - sec['sh_addr']
    # Entry for 0xe3 is at offset 0xf848
    entry_bytes = data[offset + 0xf848: offset + 0xf848 + 0x200]

# Let's inspect the fields of an entry in OIDTable
# Let's see how OIDTable entries are laid out.
# In librdm.so, let's find the function that accesses OIDTable or reads parameters
# Or let's inspect the parameter table for OID 0xe3.
print("OID 0xe3 table entry:")
for i in range(0, 128, 16):
    print(f"  +0x{i:02x}: {entry_bytes[i:i+16].hex(' ')}")


