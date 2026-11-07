import sys
import os
from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

def analyze_func(elf_path, func_name, func_addr, func_size, out_file=None):
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        
        sym_map = {}
        for sname in ['.dynsym', '.symtab']:
            sec = elf.get_section_by_name(sname)
            if sec:
                for sym in sec.iter_symbols():
                    if sym['st_value'] != 0:
                        sym_map[sym['st_value']] = sym.name

        rel_map = {}
        for rname in ['.rela.plt', '.rela.dyn']:
            rsec = elf.get_section_by_name(rname)
            symsec = elf.get_section_by_name('.dynsym')
            if rsec and symsec:
                for rel in rsec.iter_relocations():
                    s_idx = rel['r_info_sym']
                    if s_idx < symsec.num_symbols():
                        sym = symsec.get_symbol(s_idx)
                        rel_map[rel['r_offset']] = sym.name

        text_sec = None
        for sec in elf.iter_sections():
            sh_addr = sec['sh_addr']
            sh_size = sec['sh_size']
            if sh_addr <= func_addr < sh_addr + sh_size:
                text_sec = sec
                break
        
        if not text_sec:
            print(f'Cannot find section for addr 0x{func_addr:x}')
            return
            
        offset_in_sec = func_addr - text_sec['sh_addr']
        sec_data = text_sec.data()
        func_data = sec_data[offset_in_sec : offset_in_sec + func_size]
        
        rodata_sec = elf.get_section_by_name('.rodata')
        rodata_addr = rodata_sec['sh_addr'] if rodata_sec else 0
        rodata_data = rodata_sec.data() if rodata_sec else b''

        def get_rodata_str(addr):
            if rodata_addr <= addr < rodata_addr + len(rodata_data):
                offset = addr - rodata_addr
                end = rodata_data.find(b'\x00', offset)
                if end != -1:
                    try:
                        s = rodata_data[offset:end].decode('latin1')
                        # filter printable
                        if all(32 <= ord(c) < 127 for c in s):
                            return s
                    except:
                        pass
            return ''

        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        md.detail = True
        
        lines = []
        lines.append(f'=== Disassembly of {func_name} (0x{func_addr:x}, {func_size} bytes) in {os.path.basename(elf_path)} ===')
        
        reg_state = {}
        
        for insn in md.disasm(func_data, func_addr):
            comment = ''
            
            if insn.mnemonic == 'adrp':
                reg = insn.op_str.split(',')[0].strip()
                imm = insn.operands[1].imm
                reg_state[reg] = imm
            elif insn.mnemonic in ['add', 'ldr', 'ldrb', 'ldrh']:
                parts = [p.strip() for p in insn.op_str.split(',')]
                dst = parts[0]
                if len(parts) >= 2 and parts[1] in reg_state:
                    base = reg_state[parts[1]]
                    offset = 0
                    if len(parts) >= 3:
                        try:
                            off_str = parts[2].strip(' []#')
                            offset = int(off_str, 0)
                        except:
                            offset = 0
                    target_addr = base + offset
                    st = get_rodata_str(target_addr)
                    if st:
                        comment = f' ; "{st}"'
                    elif target_addr in sym_map:
                        comment = f' ; <{sym_map[target_addr]}>'
                    elif target_addr in rel_map:
                        comment = f' ; GOT: <{rel_map[target_addr]}>'
                    if insn.mnemonic == 'add':
                        reg_state[dst] = target_addr
            
            if insn.mnemonic in ['bl', 'b']:
                try:
                    target = insn.operands[0].imm
                    if target in sym_map:
                        comment = f' ; <{sym_map[target]}>'
                    elif target in rel_map:
                        comment = f' ; GOT: <{rel_map[target]}>'
                except:
                    pass
                    
            lines.append(f'0x{insn.address:08x}:  {insn.mnemonic:<8} {insn.op_str:<32} {comment}')
            
        out_str = '\n'.join(lines)
        if out_file:
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(out_str)
            print(f'Wrote {len(lines)} lines to {out_file}')
        else:
            print(out_str)

if __name__ == '__main__':
    os.makedirs(r'C:\Users\REGEN\AirtelModemRev\analysis\disasm', exist_ok=True)
    
    # 1. libcccbe.so functions
    libcccbe = r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so'
    analyze_func(libcccbe, 'libcccBeWan_eth_Init', 0x38074, 496, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\libcccBeWan_eth_Init.txt')
    analyze_func(libcccbe, 'libccc_executePPPv4Client', 0x348f4, 140, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\libccc_executePPPv4Client.txt')
    analyze_func(libcccbe, 'setWanIpPppInterfaceName', 0x346d0, 548, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\setWanIpPppInterfaceName.txt')
    analyze_func(libcccbe, 'libcccBeWan_processPPPoEPassThrough', 0x373b8, 2228, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\libcccBeWan_processPPPoEPassThrough.txt')

    # 2. libbemodules.so functions
    libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'
    analyze_func(libbemodules, 'beConfigWANByPPPoE', 0x664a8, 1712, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\beConfigWANByPPPoE.txt')
    analyze_func(libbemodules, 'pppConnection', 0x973c0, 4180, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\pppConnection.txt')
    analyze_func(libbemodules, 'pppConfigSet', 0x65f64, 1348, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\pppConfigSet.txt')
    analyze_func(libbemodules, 'beWanEnablePPPv4Client', 0x66ee4, 52, 
                 r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\beWanEnablePPPv4Client.txt')

