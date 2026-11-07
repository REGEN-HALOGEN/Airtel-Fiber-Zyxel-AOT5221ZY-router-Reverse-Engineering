import elftools.elf.elffile as elffile
import capstone

def disasm_func_around(elf_path, target_addr, before=20, count=60):
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        text = elf.get_section_by_name('.text')
        text_addr = text['sh_addr']
        text_data = text.data()
        
        dynsym = elf.get_section_by_name('.dynsym')
        syms = {}
        if dynsym:
            syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
        symtab = elf.get_section_by_name('.symtab')
        if symtab:
            for s in symtab.iter_symbols():
                syms[s.entry.st_value] = s.name
        
        # PLT symbols
        rela_plt = elf.get_section_by_name('.rela.plt')
        plt = elf.get_section_by_name('.plt')
        if rela_plt and plt:
            sym_list = [s.name for s in dynsym.iter_symbols()] if dynsym else []
            for i, rel in enumerate(rela_plt.iter_relocations()):
                p_addr = plt['sh_addr'] + 32 + i * 16
                if rel['r_info_sym'] < len(sym_list):
                    syms[p_addr] = sym_list[rel['r_info_sym']]
                    
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        
        start_addr = max(text_addr, target_addr - before * 4)
        offset = start_addr - text_addr
        size = count * 4
        code = text_data[offset:offset+size]
        
        # Find nearest symbol preceding target_addr
        prev_sym = None
        for sa, sn in sorted(syms.items()):
            if sa <= target_addr:
                prev_sym = (sa, sn)
            else:
                break
        print(f"\nDisassembling around 0x{target_addr:x} in {elf_path}:")
        if prev_sym:
            print(f"Nearest preceding symbol: 0x{prev_sym[0]:x} <{prev_sym[1]}> (+0x{target_addr - prev_sym[0]:x})")
            
        for ins in md.disasm(code, start_addr):
            sym_name = syms.get(ins.address, "")
            if sym_name:
                print(f"\n<{sym_name}>:")
            comment = ""
            if ins.mnemonic in ['bl', 'b']:
                try:
                    dest = int(ins.op_str.replace('#', ''), 16)
                    if dest in syms:
                        comment = f" <{syms[dest]}>"
                except:
                    pass
            marker = "==>" if ins.address == target_addr else "   "
            print(f"{marker} 0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str:<32}{comment}")

disasm_func_around('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 0x414b9c, before=10, count=40)

