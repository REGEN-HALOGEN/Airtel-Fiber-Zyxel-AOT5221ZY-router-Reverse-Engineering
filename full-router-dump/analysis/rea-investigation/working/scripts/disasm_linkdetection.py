import capstone
import elftools.elf.elffile as ef

path = r'c:\Users\REGEN\AirtelModemRev\files\linkdetection'

with open(path, 'rb') as f:
    elf = ef.ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    rodata_sec = elf.get_section_by_name('.rodata')
    rela_plt = elf.get_section_by_name('.rela.plt')
    dynsym = elf.get_section_by_name('.dynsym')
    plt = elf.get_section_by_name('.plt')
    
    plt_addr = plt['sh_addr']
    plt_map = {}
    for i, reloc in enumerate(rela_plt.iter_relocations()):
        sym = dynsym.get_symbol(reloc['r_info_sym'])
        stub_addr = plt_addr + 0x20 + i * 0x10
        plt_map[stub_addr] = sym.name
        
    ro_addr = rodata_sec['sh_addr']
    ro_data = rodata_sec.data()
    
    def get_string_at(addr):
        if ro_addr <= addr < ro_addr + len(ro_data):
            offset = addr - ro_addr
            end = ro_data.find(b'\x00', offset)
            if end != -1:
                try:
                    return ro_data[offset:end].decode('latin1')
                except Exception:
                    pass
        return None

    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    start_off = 0x402454 - sec_addr
    end_off = 0x403538 - sec_addr
    code = sec_data[start_off:end_off]
    
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    md.detail = True
    
    adrp_regs = {}
    
    output_lines = []
    
    for ins in md.disasm(code, 0x402454):
        comment = ''
        if ins.mnemonic == 'adrp':
            reg = ins.op_str.split(',')[0].strip()
            imm = int(ins.op_str.split('#')[1].strip(), 16)
            adrp_regs[reg] = imm
        elif ins.mnemonic == 'add':
            parts = [p.strip() for p in ins.op_str.split(',')]
            if len(parts) >= 3 and parts[1] in adrp_regs and '#' in parts[2]:
                reg = parts[0]
                base = adrp_regs[parts[1]]
                imm = int(parts[2].split('#')[1].strip(), 16)
                target_addr = base + imm
                s = get_string_at(target_addr)
                if s:
                    comment = f'; "{s}"'
                adrp_regs[reg] = target_addr
        elif ins.mnemonic == 'bl':
            if '#' in ins.op_str:
                target = int(ins.op_str.split('#')[1].strip(), 16)
                if target in plt_map:
                    comment = f'; <{plt_map[target]}>'
                    
        line = f'0x{ins.address:x}:  {ins.mnemonic:<8} {ins.op_str:<32} {comment}'
        output_lines.append(line)

with open(r'c:\Users\REGEN\AirtelModemRev\full-router-dump\analysis\rea-investigation\evidence\disassembly\linkdetection_0x402454.asm', 'w', encoding='utf-8') as out:
    out.write('\n'.join(output_lines))

print(f'Disassembled {len(output_lines)} instructions to linkdetection_0x402454.asm')

