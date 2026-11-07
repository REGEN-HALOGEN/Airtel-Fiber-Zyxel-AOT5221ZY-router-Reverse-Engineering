from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [s.name for s in dynsym.iter_symbols()]
    
    for i, r in enumerate(rela_plt.iter_relocations()):
        if r['r_offset'] == 0xe72f8:
            plt_entry = plt_base + 0x20 + i * 0x10
            print(f"beWanEnablePPPv4Client is PLT entry {i} at 0x{plt_entry:x}")
            break


