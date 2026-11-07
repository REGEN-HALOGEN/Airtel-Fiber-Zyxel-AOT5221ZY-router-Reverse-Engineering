from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
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

start = 0x664a8
size = 1712
code = text_data[start - text_base : start - text_base + size]

# Track offsets accessed relative to x20
offsets_x20 = {}
instructions = []

for insn in md.disasm(code, start):
    dis = f"{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str}"
    instructions.append((insn, dis))
    
    # check if x20 is used as base
    for op in insn.operands:
        if op.type == ARM64_OP_MEM:
            if insn.reg_name(op.mem.base) == 'x20':
                disp = op.mem.disp
                offsets_x20[disp] = f"{insn.mnemonic} {insn.op_str} at 0x{insn.address:x}"
        elif op.type == ARM64_OP_REG and insn.mnemonic == 'add':
            if len(insn.operands) >= 3 and insn.reg_name(insn.operands[1].reg) == 'x20' and insn.operands[2].type == ARM64_OP_IMM:
                disp = insn.operands[2].imm
                offsets_x20[disp] = f"add {insn.op_str} at 0x{insn.address:x}"

print(f"Total struct offsets accessed from x20: {len(offsets_x20)}")
for disp in sorted(offsets_x20.keys()):
    print(f"  +0x{disp:03x}: {offsets_x20[disp]}")
