import capstone
import elftools.elf.elffile as ef

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    elf = ef.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    sym = [s for s in dynsym.iter_symbols() if s.name == 'OIDTable'][0]
    val = sym.entry.st_value
    page = val & ~0xfff
    offset = val & 0xfff
    
    text_sec = elf.get_section_by_name('.text')
    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    insns = list(md.disasm(sec_data, sec_addr))
    
    for i, ins in enumerate(insns):
        if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
            # check next few instructions
            print(f"Ref at {hex(ins.address)}:")
            for ctx in insns[i:i+8]:
                print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")

