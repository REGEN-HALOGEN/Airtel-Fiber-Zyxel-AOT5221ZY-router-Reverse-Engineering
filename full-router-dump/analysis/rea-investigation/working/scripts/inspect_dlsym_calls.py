import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    
    dlsym_plt = None
    for i, rel in enumerate(rela_plt.iter_relocations()):
        p_addr = plt['sh_addr'] + 32 + i * 16
        if sym_list[rel['r_info_sym']] == 'dlsym':
            dlsym_plt = p_addr
            break
            
    print(f"dlsym PLT stub at 0x{dlsym_plt:x}")
    
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    calls = []
    for ins in md.disasm(text_data, text_addr):
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest == dlsym_plt:
                    calls.append(ins.address)
            except:
                pass
                
    print(f"Found {len(calls)} calls to dlsym:")
    for c in calls:
        print(f"  Call at 0x{c:x}")
        # disasm 10 instructions before call
        off = c - 40 - text_addr
        for ins in md.disasm(text_data[off:off+44], c - 40):
            print(f"    0x{ins.address:08x}: {ins.mnemonic} {ins.op_str}")
        print()

