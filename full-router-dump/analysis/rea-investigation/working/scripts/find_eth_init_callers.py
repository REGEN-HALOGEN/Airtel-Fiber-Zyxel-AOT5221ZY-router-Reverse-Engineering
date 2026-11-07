import capstone
import elftools.elf.elffile as elffile

libs = [
    'full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so',
    'full-router-dump/filesystem/rootfs/usr/bin/ccc_be'
]

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

for lib in libs:
    with open(lib, 'rb') as f:
        elf = elffile.ELFFile(f)
        text = elf.get_section_by_name('.text')
        text_addr = text['sh_addr']
        text_data = text.data()
        
        dynsym = elf.get_section_by_name('.dynsym')
        syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
        rela_plt = elf.get_section_by_name('.rela.plt')
        plt = elf.get_section_by_name('.plt')
        sym_list = [s.name for s in dynsym.iter_symbols()]
        target_plt = []
        if rela_plt and plt:
            for i, rel in enumerate(rela_plt.iter_relocations()):
                p_addr = plt['sh_addr'] + 32 + i * 16
                name = sym_list[rel['r_info_sym']]
                syms[p_addr] = name
                if 'eth_Init' in name:
                    target_plt.append(p_addr)
        
        # Also check internal address in libcccbe.so
        if 'libcccbe.so' in lib:
            target_plt.append(0x38074)
            
        print(f"=== Checking {lib} (targets: {[hex(a) for a in target_plt]}) ===")
        insns = list(cs.disasm(text_data, text_addr))
        for i, ins in enumerate(insns):
            if ins.mnemonic in ['bl', 'b']:
                try:
                    t = int(ins.op_str.replace('#', ''), 16)
                    if t in target_plt:
                        print(f"  Call at {hex(ins.address)} in {lib}: {ins.mnemonic} {ins.op_str}")
                        # print context
                        for ctx in insns[max(0, i-6):i+4]:
                            c = f" <{syms[int(ctx.op_str.replace('#', ''), 16)]}>" if ctx.mnemonic == 'bl' and int(ctx.op_str.replace('#', ''), 16) in syms else ""
                            print(f"    {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}{c}")
                except:
                    pass

