import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/bin/pppd', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    
    for r in rela_plt.iter_relocations():
        sname = sym_list[r['r_info_sym']]
        if 'rdm' in sname.lower() or 'cmsg' in sname.lower():
            print(f"pppd calls RDM/CMSG: {sname} (reloc at 0x{r['r_offset']:x})")

