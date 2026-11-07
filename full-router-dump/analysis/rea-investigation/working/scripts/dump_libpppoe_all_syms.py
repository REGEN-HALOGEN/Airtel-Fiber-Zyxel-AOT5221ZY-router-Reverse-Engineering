import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    syms = []
    for s in (symtab.iter_symbols() if symtab else []):
        if s.name:
            syms.append((s.entry.st_value, s.name))
    for s in (dynsym.iter_symbols() if dynsym else []):
        if s.name:
            syms.append((s.entry.st_value, s.name))
            
    for val, name in sorted(set(syms)):
        print(f"0x{val:08x}: {name}")

