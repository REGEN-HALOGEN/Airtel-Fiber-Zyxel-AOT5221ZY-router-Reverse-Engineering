from elftools.elf.elffile import ELFFile
import struct

# Let's inspect OIDTable entry for OID 0xe3 (227)
# In cccRdmGetOffsetByOID:
# w1 = 0xe3 (227)
# x2 = w1
# x0 = (x2 + w1*8)*4 - x2 = (9 * 227) * 4 - 227 = 227 * 35 = 7945
# x2 = [0x28fa8] (OIDTable)
# entry = OIDTable + 7945 * 8 = OIDTable + 63560 = OIDTable + 0xf848!
# EXACTLY 0xf848 which we found earlier!
# Each entry in OIDTable is 35 * 8 = 280 (0x118) bytes!

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= 0x294f0 < s['sh_addr'] + s['sh_size']:
            sec = s
            break
            
    data = sec.data()
    offset = 0x294f0 - sec['sh_addr']
    entry = data[offset + 0xf848: offset + 0xf848 + 280]

print(f"OID 0xe3 entry size: {len(entry)} bytes")
# Let's unpack fields of this entry:
# struct OIDTableEntry:
# +0x00: OID (uint64)
# +0x08: parentOID / flags?
# +0x10: name (char[?])
# +0x20: paramNamesOffset (uint64)
# +0x28: paramTypesOffset (uint64)
# +0x30: paramOffsetsOffset (uint64)
# ...
for i in range(0, 128, 8):
    val = struct.unpack('<Q', entry[i:i+8])[0]
    print(f"  +0x{i:02x}: 0x{val:016x} ({val})")

# Let's check string at +0x10 or +0x11
print("String at +0x10:", entry[16:64])


