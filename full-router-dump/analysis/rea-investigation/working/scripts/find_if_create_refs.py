import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    
    target = b'--if-create-name'
    idx = 0
    matches = []
    while True:
        idx = data.find(target, idx)
        if idx == -1:
            break
        str_addr = addr + idx
        end = data.find(b'\x00', idx)
        # Find start of string (look backward for null byte)
        start = data.rfind(b'\x00', 0, idx)
        start = 0 if start == -1 else start + 1
        full_str = data[start:end].decode('latin1', 'replace')
        print(f"String at 0x{addr+start:x}: \"{full_str}\"")
        matches.append(addr+start)
        idx = end + 1
        
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

    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    for m in matches:
        page = m & ~0xfff
        offset = m & 0xfff
        prev = None
        for ins in md.disasm(text_data, text_addr):
            if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
                prev = ins
            elif prev and ins.address == prev.address + 4:
                if hex(offset) in ins.op_str:
                    func = None
                    for sa, sn in sorted(syms.items()):
                        if sa <= ins.address:
                            func = (sa, sn)
                        else:
                            break
                    fn_name = f"{func[1]}+0x{ins.address-func[0]:x}" if func else "unknown"
                    print(f"  Referenced at 0x{ins.address:x} in {fn_name}")
                prev = None
            else:
                prev = None

