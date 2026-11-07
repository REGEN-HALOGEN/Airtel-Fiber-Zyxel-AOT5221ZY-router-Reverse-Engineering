import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    for s in elf.iter_sections():
        if s['sh_addr'] <= 0x4784d < s['sh_addr'] + s['sh_size']:
            print("0x4784d is in section:", s.name)
        if s['sh_addr'] <= 0x4c1e5 < s['sh_addr'] + s['sh_size']:
            print("0x4c1e5 is in section:", s.name)

