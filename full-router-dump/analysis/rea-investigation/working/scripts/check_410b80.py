import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    syms = {}
    if symtab:
        for s in symtab.iter_symbols():
            if s.name:
                syms[s.entry.st_value] = s.name
    if dynsym:
        for s in dynsym.iter_symbols():
            if s.name:
                syms[s.entry.st_value] = s.name
                
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    if rela_plt and plt:
        sym_list = [s.name for s in dynsym.iter_symbols()]
        for i, rel in enumerate(rela_plt.iter_relocations()):
            p_addr = plt['sh_addr'] + 32 + i * 16
            if rel['r_info_sym'] < len(sym_list):
                syms[p_addr] = sym_list[rel['r_info_sym']]

    print("0x410b80:", syms.get(0x410b80, "unknown"))

