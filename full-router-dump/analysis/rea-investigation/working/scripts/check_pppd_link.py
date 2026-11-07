import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/bin/pppd', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    
    target_plt = None
    if rela_plt and plt:
        for i, rel in enumerate(rela_plt.iter_relocations()):
            if sym_list[rel['r_info_sym']] == 'get_sockaddr_ll':
                target_plt = plt['sh_addr'] + 32 + i * 16
                break
                
    print("get_sockaddr_ll in pppd PLT:", hex(target_plt) if target_plt else "None")
    
    # Check if pppd links to libpppoe.so
    dynamic = elf.get_section_by_name('.dynamic')
    for tag in dynamic.iter_tags():
        if tag.entry.d_tag == 'DT_NEEDED':
            print("DT_NEEDED:", tag.needed)

