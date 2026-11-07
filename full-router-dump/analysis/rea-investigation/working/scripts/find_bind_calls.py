import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    
    bind_plt = None
    for i, rel in enumerate(rela_plt.iter_relocations()):
        if sym_list[rel['r_info_sym']] == 'bind':
            bind_plt = plt['sh_addr'] + 32 + i * 16
            break
            
    print("bind PLT stub at:", hex(bind_plt) if bind_plt else "None")
    
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    for ins in md.disasm(text_data, text_addr):
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest == bind_plt:
                    print(f"Call to bind from 0x{ins.address:x}")
            except:
                pass

