from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    for s in dynsym.iter_symbols():
        if s['st_info']['type'] == 'STT_FUNC' and s['st_size'] > 0:
            if 'init' in s.name.lower() or 'configloader' in s.name.lower() or 'reg' in s.name.lower():
                print(f"0x{s['st_value']:x} (size {s['st_size']:4d}): {s.name}")


