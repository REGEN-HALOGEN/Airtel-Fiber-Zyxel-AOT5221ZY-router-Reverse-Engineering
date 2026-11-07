from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

start_addr = 0x0e9e8
size = 200
code = text_data[start_addr - text_base : start_addr - text_base + size]

for insn in md.disasm(code, start_addr):
    print(f"0x{insn.address:05x}: {insn.mnemonic:8s} {insn.op_str}")


