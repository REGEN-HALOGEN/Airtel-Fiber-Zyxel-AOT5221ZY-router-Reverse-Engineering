from elftools.elf.elffile import ELFFile

for bin_path in [r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so', r'full-router-dump\filesystem\rootfs\usr\bin\ccc_be']:
    with open(bin_path, 'rb') as f:
        elf = ELFFile(f)
        rela_dyn = elf.get_section_by_name('.rela.dyn')
        dynsym = elf.get_section_by_name('.dynsym')
        sym_names = [s.name for s in dynsym.iter_symbols()] if dynsym else []
        for r in rela_dyn.iter_relocations():
            if r['r_addend'] == 0x664a8:
                print(f"Reloc with addend 0x664a8 in {bin_path} at offset 0x{r['r_offset']:x}")
            sym_idx = r['r_info_sym']
            if sym_idx < len(sym_names) and sym_names[sym_idx] == 'beConfigWANByPPPoE':
                print(f"Reloc to symbol beConfigWANByPPPoE in {bin_path} at offset 0x{r['r_offset']:x}")


