import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    sym_map = {}
    for s in (symtab.iter_symbols() if symtab else []):
        sym_map[s.name] = s.entry.st_value
    for s in (dynsym.iter_symbols() if dynsym else []):
        sym_map[s.name] = s.entry.st_value
        
    addr = sym_map.get('checkWANDeviceObjectRequestedLinkIsUp', 0)
    print("checkWANDeviceObjectRequestedLinkIsUp at 0x%x" % addr)
    
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    off = addr - text_addr
    for ins in md.disasm(text_data[off:off+0x100], addr):
        print(f"0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str:<32}")
        if ins.mnemonic == 'ret':
            break

