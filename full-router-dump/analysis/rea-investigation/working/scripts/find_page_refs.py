import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    syms = {}
    for s in (symtab.iter_symbols() if symtab else []):
        syms[s.entry.st_value] = s.name
    for s in (dynsym.iter_symbols() if dynsym else []):
        syms[s.entry.st_value] = s.name

    for page in [0x47000, 0x4c000]:
        print(f"\n--- References to page {hex(page)} ---")
        prev = None
        for ins in md.disasm(text_data, text_addr):
            if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
                prev = ins
            elif prev and ins.address == prev.address + 4:
                # print instruction
                func = None
                for sa, sn in sorted(syms.items()):
                    if sa <= ins.address:
                        func = (sa, sn)
                    else:
                        break
                fn_name = f"{func[1]}+0x{ins.address-func[0]:x}" if func else "unknown"
                print(f"  0x{prev.address:x}: {prev.mnemonic} {prev.op_str}; 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}  [{fn_name}]")
                prev = None
            else:
                prev = None

