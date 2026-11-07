import sys
import os
from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

def analyze_func(elf_path, func_name, func_addr, func_size):
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        
        # Build symbol map
        sym_map = {}
        for sname in ['.dynsym', '.symtab']:
            sec = elf.get_section_by_name(sname)
            if sec:
                for sym in sec.iter_symbols():
                    if sym['st_value'] != 0:
                        sym_map[sym['st_value']] = sym.name

        # Build PLT relocation map
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

        # Find section containing func_addr
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
        
        # Read rodata for string resolution
        rodata_sec = elf.get_section_by_name('.rodata')
        rodata_addr = rodata_sec['sh_addr'] if rodata_sec else 0
        rodata_data = rodata_sec.data() if rodata_sec else b''

        def get_rodata_str(addr):
            if rodata_addr <= addr < rodata_addr + len(rodata_data):
                offset = addr - rodata_addr
                end = rodata_data.find(b'\x00', offset)
                if end != -1:
                    try:
                        return rodata_data[offset:end].decode('latin1')
                    except:
                        return ''
            return ''

        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        md.detail = True
        
        print(f'=== Disassembly of {func_name} (0x{func_addr:x}, {func_size} bytes) in {os.path.basename(elf_path)} ===')
        
        reg_state = {}
        
        for insn in md.disasm(func_data, func_addr):
            comment = ''
            
            # Track ADRP
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
            
            # Check branches
            if insn.mnemonic in ['bl', 'b']:
                try:
                    target = insn.operands[0].imm
                    if target in sym_map:
                        comment = f' ; <{sym_map[target]}>'
                except:
                    pass
                    
            print(f'0x{insn.address:08x}:  {insn.mnemonic:<8} {insn.op_str:<32} {comment}')

if __name__ == '__main__':
    targets = [
        (r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'libcccBeWan_eth_Init', 0x38074, 496),
        (r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'libccc_executePPPv4Client', 0x348f4, 140),
        (r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'setWanIpPppInterfaceName', 0x346d0, 548),
        (r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'libcccBeWan_createWANPPPConnectionCfgFile_wrapper', 0x373a4, 8),
    ]
    for p, n, a, s in targets:
        analyze_func(p, n, a, s)
        print('\n' + '='*70 + '\n')

