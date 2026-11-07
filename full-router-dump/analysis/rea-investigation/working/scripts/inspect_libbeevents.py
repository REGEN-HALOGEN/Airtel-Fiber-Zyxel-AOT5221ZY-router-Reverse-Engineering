import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    
    print("=== Symbols in libbeEvents.so ===")
    for v, n in sorted(syms.items()):
        if any(k in n for k in ['Event', 'Wan', 'ppp', '206', 'Up', 'Down', 'event']):
            print(f"  {hex(v)}: {n}")

