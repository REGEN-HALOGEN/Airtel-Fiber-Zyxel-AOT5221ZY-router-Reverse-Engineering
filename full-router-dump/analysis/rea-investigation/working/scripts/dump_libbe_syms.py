import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [(s.entry.st_value, s.name) for s in dynsym.iter_symbols() if s['st_shndx'] != 'SHN_UNDEF']
    for val, name in sorted(syms):
        print(f"0x{val:08x}: {name}")

