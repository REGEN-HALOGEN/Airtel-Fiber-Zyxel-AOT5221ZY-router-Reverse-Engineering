import elftools.elf.elffile as elffile
import capstone

def find_func_callers(elf_path, sym_name):
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        symtab = elf.get_section_by_name('.symtab')
        syms = {}
        target_val = None
        for s in (symtab.iter_symbols() if symtab else []):
            syms[s.entry.st_value] = s.name
            if s.name == sym_name:
                target_val = s.entry.st_value
        for s in (dynsym.iter_symbols() if dynsym else []):
            syms[s.entry.st_value] = s.name
            if s.name == sym_name:
                target_val = s.entry.st_value
                
        rela_plt = elf.get_section_by_name('.rela.plt')
        plt = elf.get_section_by_name('.plt')
        plt_target = None
        if rela_plt and plt:
            sym_list = [s.name for s in dynsym.iter_symbols()]
            for i, rel in enumerate(rela_plt.iter_relocations()):
                if sym_list[rel['r_info_sym']] == sym_name:
                    plt_target = plt['sh_addr'] + 32 + i * 16
                    break

        text = elf.get_section_by_name('.text')
        text_data = text.data()
        text_addr = text['sh_addr']
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        print(f"Searching callers of {sym_name} in {elf_path}: (func: {hex(target_val) if target_val else 'None'}, plt: {hex(plt_target) if plt_target else 'None'})")
        for ins in md.disasm(text_data, text_addr):
            if ins.mnemonic in ['bl', 'b']:
                try:
                    dest = int(ins.op_str.replace('#', ''), 16)
                    if (target_val and dest == target_val) or (plt_target and dest == plt_target):
                        func = None
                        for sa, sn in sorted(syms.items()):
                            if sa <= ins.address:
                                func = (sa, sn)
                            else:
                                break
                        fn_name = f"{func[1]}+0x{ins.address-func[0]:x}" if func else "unknown"
                        print(f"  Called from 0x{ins.address:x} in {fn_name}")
                except:
                    pass

find_func_callers('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'createLayer3Interface')
find_func_callers('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'createLayer3Interface')

