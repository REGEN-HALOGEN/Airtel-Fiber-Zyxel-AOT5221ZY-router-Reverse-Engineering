import os
from elftools.elf.elffile import ELFFile
from capstone import *

def check_binary(bin_path):
    print(f"\n================ Checking {bin_path} ================")
    with open(bin_path, 'rb') as f:
        elf = ELFFile(f)
        rodata = elf.get_section_by_name('.rodata')
        if not rodata:
            return
        ro_data = rodata.data()
        ro_addr = rodata['sh_addr']
        
        target = b'X_5067F0_IfName\x00'
        idx = ro_data.find(target)
        if idx == -1:
            print("String not in .rodata")
            return
        str_addr = ro_addr + idx
        print(f"String at 0x{str_addr:x}")
        
        text_sec = elf.get_section_by_name('.text')
        text_data = text_sec.data()
        text_base = text_sec['sh_addr']
        
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        md.detail = True
        
        regs = {}
        for insn in md.disasm(text_data, text_base):
            if insn.mnemonic == 'adrp':
                regs[insn.operands[0].reg] = insn.operands[1].imm
            elif insn.mnemonic == 'add':
                if len(insn.operands) >= 3 and insn.operands[1].type == 1 and insn.operands[2].type == 2:
                    src = insn.operands[1].reg
                    if src in regs:
                        tgt = regs[src] + insn.operands[2].imm
                        if tgt == str_addr:
                            print(f"  XREF at 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
            elif insn.mnemonic in ['b', 'ret']:
                regs.clear()

check_binary(r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so')
check_binary(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so')


