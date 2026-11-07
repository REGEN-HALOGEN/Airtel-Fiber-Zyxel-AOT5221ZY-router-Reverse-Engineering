import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    
    for target in [0x2620, 0x2670, 0x2850, 0x2880]:
        idx = (target - (plt['sh_addr'] + 32)) // 16
        for i, rel in enumerate(rela_plt.iter_relocations()):
            if i == idx:
                print(f"0x{target:x} is PLT stub for: {sym_list[rel['r_info_sym']]}")

