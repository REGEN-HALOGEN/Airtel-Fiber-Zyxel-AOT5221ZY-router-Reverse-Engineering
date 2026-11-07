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
    start_addr = 0x50348
    offset = start_addr - text_addr
    # let's search for all `bl` calls in L0ConfigLoad (from 0x50348 to 0x50858)
    code = text_data[offset:offset+(0x50858 - 0x50348)]
    print("=== Subroutine calls inside L0ConfigLoad (0x50348 - 0x50858) ===")
    for ins in md.disasm(code, start_addr):
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest in syms:
                    print(f"0x{ins.address:08x}: {ins.mnemonic:<4} {ins.op_str:<24} <{syms[dest]}>")
                elif dest >= text_addr and dest < text_addr + len(text_data):
                    pass
            except:
                pass

