import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
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
    m = 0xbdab0
    page = m & ~0xfff
    offset = m & 0xfff
    print(f"Searching refs for 0x{m:x} (page 0x{page:x}, offset 0x{offset:x})")
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

