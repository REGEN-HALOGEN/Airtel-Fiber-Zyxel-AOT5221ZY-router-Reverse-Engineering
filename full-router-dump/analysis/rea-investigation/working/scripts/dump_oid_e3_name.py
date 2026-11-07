from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= 0x294f0 < s['sh_addr'] + s['sh_size']:
            sec = s
            break
            
    data = sec.data()
    offset = 0x294f0 - sec['sh_addr']
    entry_bytes = data[offset + 0xf848: offset + 0xf848 + 0x200]
    # In OIDTable, let's see how string is stored:
    # Notice bytes 16..: 01 followed by ascii string
    name_bytes = entry_bytes[17:]
    name = name_bytes.split(b'\x00')[0]
    print(f"OID 0xe3 object path: {name.decode('latin1')}")


