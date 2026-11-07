import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    symbols = []
    for s in (dynsym.iter_symbols() if dynsym else []):
        if s.name:
            symbols.append((s.entry.st_value, s.name))
    if symtab:
        for s in symtab.iter_symbols():
            if s.name:
                symbols.append((s.entry.st_value, s.name))
                
    symbols = sorted(set(symbols), key=lambda x: x[0])
    
    print(f"Total symbols: {len(symbols)}")
    print("\nCallbacks matching WAN / PPP / Layer3:")
    for addr, name in symbols:
        nl = name.lower()
        if ('wan' in nl or 'ppp' in nl or 'layer3' in nl or 'eth' in nl) and ('changed' in nl or 'configload' in nl or 'event' in nl or 'action' in nl or 'init' in nl):
            print(f"0x{addr:08x}: {name}")

