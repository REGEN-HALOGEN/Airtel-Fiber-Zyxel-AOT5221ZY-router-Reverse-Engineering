import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rela = elf.get_section_by_name('.rela.dyn')
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    for r in rela.iter_relocations():
        if r['r_offset'] == 0xe6cf0:
            sym_name = sym_list[r['r_info_sym']] if r['r_info_sym'] < len(sym_list) else ""
            print(f"Relocation at 0xe6cf0: {sym_name} + 0x{r['r_addend']:x}")

