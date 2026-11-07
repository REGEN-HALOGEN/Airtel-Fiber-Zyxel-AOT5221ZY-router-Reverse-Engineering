import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    
    idx = (0x1d340 - (plt['sh_addr'] + 32)) // 16
    for i, rel in enumerate(rela_plt.iter_relocations()):
        if i == idx:
            print(f"0x1d340 is PLT stub for: {sym_list[rel['r_info_sym']]}")

