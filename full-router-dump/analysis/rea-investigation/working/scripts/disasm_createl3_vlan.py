from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libcccbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so'

with open(libcccbe_path, 'rb') as f:
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

start = 0x35814
size = 200
code = text_data[start - text_base : start - text_base + size]

regs = {}
print("Disassembly of createLayer3Interface (VLAN tagged branch 0x35814):")
for insn in md.disasm(code, start):
    comment = ""
    if insn.mnemonic == 'adrp':
        regs[insn.operands[0].reg] = insn.operands[1].imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].type == 1 and insn.operands[2].type == 2:
            src = insn.operands[1].reg
            if src in regs:
                tgt = regs[src] + insn.operands[2].imm
                s = get_rodata_str(tgt)
                if s: comment = f" // \"{s}\""
    elif insn.mnemonic in ['b', 'ret']:
        regs.clear()
        
    print(f"0x{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str:32s} {comment}")


