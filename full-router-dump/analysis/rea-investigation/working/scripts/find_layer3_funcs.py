from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    for s in dynsym.iter_symbols():
        if 'layer3' in s.name.lower() or 'action' in s.name.lower() or 'wan' in s.name.lower():
            if 'do' in s.name.lower() or 'interface' in s.name.lower():
                print(f"0x{s['st_value']:x} (size {s['st_size']:4d}): {s.name}")


