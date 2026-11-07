import capstone
import elftools.elf.elffile as ef

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    elf = ef.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.name: s.entry.st_value for s in dynsym.iter_symbols()}
    
    text_sec = elf.get_section_by_name('.text')
    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    for name in ['cccRdmAddIndexChildObject', 'cccRdmAddObjectWithAssignIA']:
        addr = syms[name]
        print(f"\n==========================================")
        print(f"Function: {name} at {hex(addr)}")
        print(f"==========================================")
        offset = addr - sec_addr
        # Disassemble first 60 instructions
        code = sec_data[offset:offset+300]
        for ins in md.disasm(code, addr):
            # check if branch or call
            comment = ""
            if ins.mnemonic == 'bl':
                target = int(ins.op_str.replace('#', ''), 16)
                for s_name, s_addr in syms.items():
                    if s_addr == target:
                        comment = f" <{s_name}>"
                        break
            print(f"  {hex(ins.address)}: {ins.mnemonic} {ins.op_str}{comment}")
            if ins.mnemonic == 'ret' and ins.address > addr + 0x20:
                # break if ret reached
                pass

