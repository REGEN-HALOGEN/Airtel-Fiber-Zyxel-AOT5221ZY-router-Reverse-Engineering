from elftools.elf.elffile import ELFFile

for p in [r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so', r'full-router-dump\filesystem\rootfs\usr\bin\ccc_be']:
    with open(p, 'rb') as f:
        elf = ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        sym_names = [s.name for s in dynsym.iter_symbols()] if dynsym else []
        for sec_name in ['.rela.dyn', '.rela.plt']:
            sec = elf.get_section_by_name(sec_name)
            if sec:
                for r in sec.iter_relocations():
                    sym_idx = r['r_info_sym']
                    if sym_idx < len(sym_names) and sym_names[sym_idx] == 'beConfigWANByPPPoE':
                        print(f"Reloc to beConfigWANByPPPoE in {p} ({sec_name}) at 0x{r['r_offset']:x}")


