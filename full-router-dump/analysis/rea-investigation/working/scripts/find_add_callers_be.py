import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/usr/bin/ccc_be'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    rela_plt = elf.get_section_by_name('.rela.plt')
    dynsym = elf.get_section_by_name('.dynsym')
    plt = elf.get_section_by_name('.plt')
    text = elf.get_section_by_name('.text')
    
    symbols = [sym.name for sym in dynsym.iter_symbols()]
    
    plt_addrs = {}
    for i, rel in enumerate(rela_plt.iter_relocations()):
        sym_name = symbols[rel['r_info_sym']]
        plt_addr = plt['sh_addr'] + 32 + i * 16
        plt_addrs[plt_addr] = sym_name
        if 'Add' in sym_name or 'Del' in sym_name or 'cmsgParseAction' in sym_name:
            print(f"Target PLT: {hex(plt_addr)} -> {sym_name}")

    text_data = text.data()
    text_addr = text['sh_addr']

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

for i, insn in enumerate(insns):
    if insn.mnemonic == 'bl':
        target = int(insn.op_str.replace('#', ''), 16)
        if target in plt_addrs and ('Add' in plt_addrs[target] or 'Del' in plt_addrs[target]):
            sym_name = plt_addrs[target]
            print(f"\nCall to {sym_name} at {hex(insn.address)}:")
            start = max(0, i - 15)
            end = min(len(insns), i + 20)
            for ctx in insns[start:end]:
                comment = ""
                if ctx.mnemonic == 'bl':
                    t = int(ctx.op_str.replace('#', ''), 16)
                    if t in plt_addrs:
                        comment = f" <{plt_addrs[t]}>"
                print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}{comment}")

