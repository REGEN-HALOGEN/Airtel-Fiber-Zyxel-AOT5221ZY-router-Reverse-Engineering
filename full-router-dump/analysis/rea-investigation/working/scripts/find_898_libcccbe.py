from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libcccbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so'

with open(libcccbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

# Search for offset 0x898 (X_5067F0_IfName) in libcccbe.so .text
print("Searching for immediate 0x898 in libcccbe.so .text:")
matches = []
for insn in md.disasm(text_data, text_base):
    for op in insn.operands:
        if op.type == ARM64_OP_IMM and op.imm == 0x898:
            matches.append(insn)

for insn in matches:
    print(f"  0x{insn.address:x}: {insn.mnemonic:8s} {insn.op_str}")


