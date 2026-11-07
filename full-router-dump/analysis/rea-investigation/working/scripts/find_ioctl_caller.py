import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    syms = {}
    for s in (symtab.iter_symbols() if symtab else []):
        syms[s.entry.st_value] = s.name
    for s in (dynsym.iter_symbols() if dynsym else []):
        syms[s.entry.st_value] = s.name
        
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    # find callers of 0x4d30 or prologue
    # Prologue for 0x4d30
    prologue = None
    for a in range(0x4d30, 0x4c00, -4):
        off = a - text_addr
        for ins in md.disasm(text_data[off:off+4], a):
            if ins.mnemonic == 'stp' and 'x29, x30, [sp' in ins.op_str:
                prologue = a
                break
        if prologue:
            break
            
    print(f"Function prologue at 0x{prologue:x} ({syms.get(prologue, 'unnamed')})")
    
    # callers of prologue
    for ins in md.disasm(text_data, text_addr):
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest == prologue:
                    print(f"Called from 0x{ins.address:x}")
            except:
                pass

