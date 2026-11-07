import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    sections = [s for s in [dynsym, symtab] if s]
    target = 0x50ed4
    best = None
    for s in sections:
        for sym in s.iter_symbols():
            val = sym['st_value']
            size = sym['st_size']
            if val <= target < val + size:
                best = (val, size, sym.name)
                break
    print("Enclosing function:", best)

