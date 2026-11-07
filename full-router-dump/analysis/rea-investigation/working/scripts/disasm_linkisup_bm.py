import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    syms = {}
    for s in (symtab.iter_symbols() if symtab else []):
        syms[s.entry.st_value] = s.name
    for s in (dynsym.iter_symbols() if dynsym else []):
        syms[s.entry.st_value] = s.name
        
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    if rela_plt and plt:
        sym_list = [s.name for s in dynsym.iter_symbols()]
        for i, rel in enumerate(rela_plt.iter_relocations()):
            p_addr = plt['sh_addr'] + 32 + i * 16
            if rel['r_info_sym'] < len(sym_list):
                syms[p_addr] = sym_list[rel['r_info_sym']]

    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    start_addr = 0x67964
    offset = start_addr - text_addr
    code = text_data[offset:offset+0x180]
    for ins in md.disasm(code, start_addr):
        comment = ""
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest in syms:
                    comment = f" <{syms[dest]}>"
            except:
                pass
        print(f"0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str:<32}{comment}")
        if ins.mnemonic == 'ret':
            print("--- RET ---")
            break

