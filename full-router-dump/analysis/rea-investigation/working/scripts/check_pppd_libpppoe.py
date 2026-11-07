import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/bin/pppd', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    
    with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f2:
        elf2 = elffile.ELFFile(f2)
        dynsym2 = elf2.get_section_by_name('.dynsym')
        libpppoe_exports = set(s.name for s in dynsym2.iter_symbols() if s['st_shndx'] != 'SHN_UNDEF')
        
    for r in rela_plt.iter_relocations():
        sname = sym_list[r['r_info_sym']]
        if sname in libpppoe_exports:
            print(f"pppd calls libpppoe function: {sname} (reloc at 0x{r['r_offset']:x})")

