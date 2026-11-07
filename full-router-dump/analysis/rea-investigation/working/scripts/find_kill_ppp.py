import elftools.elf.elffile as elffile

for path in [
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so'
]:
    with open(path, 'rb') as f:
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
                
        print(f"--- Symbols in {path} matching ppp and (kill or disable or stop) ---")
        for val, name in sorted(set(syms)):
            nl = name.lower()
            if 'ppp' in nl and ('kill' in nl or 'disable' in nl or 'stop' in nl or 'down' in nl):
                print(f"  0x{val:08x}: {name}")

