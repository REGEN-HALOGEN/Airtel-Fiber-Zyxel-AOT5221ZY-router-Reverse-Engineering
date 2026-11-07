import capstone
import elftools.elf.elffile as ef

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    elf = ef.ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    start_addr = 0x13540
    offset = start_addr - sec_addr
    code = sec_data[offset:offset+0x300]
    
    # get symbols for comments
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    
    for ins in md.disasm(code, start_addr):
        comment = ""
        if ins.mnemonic == 'bl':
            target = int(ins.op_str.replace('#', ''), 16)
            if target in syms:
                comment = f" <{syms[target]}>"
        print(f"  {hex(ins.address)}: {ins.mnemonic} {ins.op_str}{comment}")

