import os, json
from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(r'full-router-dump\analysis\rea-investigation\working\scripts\libcmd_symbols.json') as f:
    sym_data = json.load(f)
    plt_map = {int(k): v for k, v in sym_data['plt'].items()}
    got_map = {int(k): v for k, v in sym_data['got'].items()}

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    
    rodata_sec = elf.get_section_by_name('.rodata')
    rodata_data = rodata_sec.data()
    rodata_base = rodata_sec['sh_addr']

def get_rodata_str(addr):
    if rodata_base <= addr < rodata_base + len(rodata_data):
        offset = addr - rodata_base
        end = rodata_data.find(b'\x00', offset)
        if end != -1:
            try:
                return rodata_data[offset:end].decode('latin1')
            except:
                return str(rodata_data[offset:end])
    return ""

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

def disasm_func(start_addr, end_addr, title):
    offset = start_addr - text_base
    size = end_addr - start_addr
    code = text_data[offset:offset+size]
    
    regs = {}
    print(f"\n================ {title} (0x{start_addr:x} - 0x{end_addr:x}) ================")
    for insn in md.disasm(code, start_addr):
        comment = ""
        # Check ADRP
        if insn.mnemonic == 'adrp':
            reg = insn.operands[0].reg
            imm = insn.operands[1].imm
            regs[reg] = imm
        elif insn.mnemonic == 'add':
            if len(insn.operands) >= 3 and insn.operands[1].type == ARM64_OP_REG and insn.operands[2].type == ARM64_OP_IMM:
                src_reg = insn.operands[1].reg
                if src_reg in regs:
                    target_addr = regs[src_reg] + insn.operands[2].imm
                    dst_reg = insn.operands[0].reg
                    regs[dst_reg] = target_addr
                    s = get_rodata_str(target_addr)
                    if s:
                        comment = f" // \"{s}\""
            else:
                dst_reg = insn.operands[0].reg
                if dst_reg in regs:
                    del regs[dst_reg]
        elif insn.mnemonic == 'ldr':
            if len(insn.operands) >= 2 and insn.operands[1].type == ARM64_OP_MEM:
                mem = insn.operands[1].mem
                if mem.base in regs:
                    target_addr = regs[mem.base] + mem.disp
                    if target_addr in got_map:
                        comment = f" // GOT -> {got_map[target_addr]}"
                    else:
                        comment = f" // [0x{target_addr:x}]"
            dst_reg = insn.operands[0].reg
            if dst_reg in regs:
                del regs[dst_reg]
        elif insn.mnemonic in ['b', 'ret']:
            regs.clear()
        elif insn.mnemonic == 'bl':
            target = insn.operands[0].imm
            if target in plt_map:
                comment = f" // <{plt_map[target]}@plt>"
            elif target in plt_map.values():
                comment = f" // <{target}>"
                
        print(f"0x{insn.address:06x}:  {insn.mnemonic:8s} {insn.op_str:32s} {comment}")

disasm_func(0x4945c, 0x49784, "CheckAndRestartPPP")
disasm_func(0x49784, 0x4997c, "wrapperDoPPP")


