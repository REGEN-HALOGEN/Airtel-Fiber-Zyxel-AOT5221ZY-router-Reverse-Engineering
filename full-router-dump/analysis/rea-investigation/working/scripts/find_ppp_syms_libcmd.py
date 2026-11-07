from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    for s in dynsym.iter_symbols():
        if 'ppp' in s.name.lower():
            print(f"Symbol {s.name}: value=0x{s['st_value']:x}, size={s['st_size']}, binding={s['st_info']['bind']}, type={s['st_info']['type']}")


