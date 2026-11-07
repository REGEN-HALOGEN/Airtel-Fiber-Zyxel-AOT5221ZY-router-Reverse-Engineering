import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    sections = [s for s in [dynsym, symtab] if s]
    matches = []
    for s in sections:
        for sym in s.iter_symbols():
            if 'WANDevice' in sym.name or 'WANConnectionDevice' in sym.name or 'WANPPPConnection' in sym.name:
                matches.append((hex(sym['st_value']), sym.name))
    
    matches.sort()
    for v, n in set(matches):
        print(f"  {v}: {n}")

