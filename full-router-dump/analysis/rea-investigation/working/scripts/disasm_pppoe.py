import capstone
import elftools.elf.elffile as ef

p = r'c:\Users\REGEN\AirtelModemRev\files\libbemodules.so'

with open(p, 'rb') as f:
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
    
    def get_str(addr):
        if ro_addr <= addr < ro_addr + len(ro_data):
            off = addr - ro_addr
            end = ro_data.find(b'\x00', off)
            return ro_data[off:end].decode('latin1')
        return ''

    sec_addr = text_sec['sh_addr']
    sec_data = text_sec.data()
    
    # 0x664a8: beConfigWANByPPPoE
    offset = 0x664a8 - sec_addr
    code = sec_data[offset:offset+0x900]
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    adrp_base = 0
    lines = []
    for ins in md.disasm(code, 0x664a8):
        c = ''
        if ins.mnemonic == 'adrp':
            adrp_base = int(ins.op_str.split('#')[1], 16)
        elif ins.mnemonic == 'add' and '#' in ins.op_str:
            parts = ins.op_str.split(',')
            if len(parts) >= 3 and '#' in parts[2]:
                imm = int(parts[2].split('#')[1], 16)
                s = get_str(adrp_base + imm)
                if s: c = f'; "{s}"'
        elif ins.mnemonic == 'bl' and '#' in ins.op_str:
            target = int(ins.op_str.split('#')[1], 16)
            if target in plt_map:
                c = f'; <{plt_map[target]}>'
        lines.append(f'0x{ins.address:x}: {ins.mnemonic:<8} {ins.op_str:<32} {c}')
        if ins.mnemonic == 'ret' and ins.address > 0x66a00:
            break

with open(r'c:\Users\REGEN\AirtelModemRev\full-router-dump\analysis\rea-investigation\evidence\disassembly\beConfigWANByPPPoE.asm', 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines))

print(f'Disassembled {len(lines)} instructions to beConfigWANByPPPoE.asm')

