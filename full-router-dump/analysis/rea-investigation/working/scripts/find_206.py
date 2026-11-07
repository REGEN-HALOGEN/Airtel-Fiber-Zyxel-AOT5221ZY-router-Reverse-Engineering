import capstone
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()
    
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    
cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

for i, ins in enumerate(insns):
    if ins.mnemonic == 'cmp' and ('#0xce' in ins.op_str or '#206' in ins.op_str):
        print(f"Match at {hex(ins.address)}: {ins.mnemonic} {ins.op_str}")
        # find enclosing function
        func_name = "unknown"
        for v in sorted(syms.keys()):
            if v <= ins.address:
                func_name = syms[v]
            else:
                break
        print(f"  In function: {func_name}")
        for ctx in insns[max(0, i-5):i+15]:
            print(f"    {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")

