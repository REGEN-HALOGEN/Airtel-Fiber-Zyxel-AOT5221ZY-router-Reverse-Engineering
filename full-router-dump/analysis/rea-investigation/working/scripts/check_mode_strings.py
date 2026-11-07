with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    data = f.read()

import elftools.elf.elffile as elffile
with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()

for a in [0xab9a8, 0xb42c8, 0xb42d0, 0xb42f8]:
    off = a - ro_addr
    s = ro_data[off:off+50].split(b'\x00')[0]
    print(f"{hex(a)}: '{s.decode('latin1', errors='replace')}'")

