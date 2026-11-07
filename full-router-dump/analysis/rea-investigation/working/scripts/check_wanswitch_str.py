with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    data = f.read()

import elftools.elf.elffile as elffile
with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()

off = 0xb414b - ro_addr
print("String at 0xb414b:", ro_data[off:off+100])

