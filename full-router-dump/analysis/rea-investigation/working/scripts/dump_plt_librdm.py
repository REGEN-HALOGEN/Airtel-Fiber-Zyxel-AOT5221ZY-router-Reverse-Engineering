import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    plt = elf.get_section_by_name('.plt')
    rela_plt = elf.get_section_by_name('.rela.plt')
    dynsym = elf.get_section_by_name('.dynsym')
    
    symbols = [sym.name for sym in dynsym.iter_symbols()]
    
    relocs = []
    for rel in rela_plt.iter_relocations():
        sym_idx = rel['r_info_sym']
        relocs.append((rel['r_offset'], symbols[sym_idx]))
    
    print("PLT mappings in librdm.so:")
    for i, (got_off, sym_name) in enumerate(relocs):
        plt_addr = plt['sh_addr'] + 32 + i * 16
        print(f"  {hex(plt_addr)} -> {sym_name}")

