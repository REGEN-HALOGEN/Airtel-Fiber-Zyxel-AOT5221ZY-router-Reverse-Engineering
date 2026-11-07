from elftools.elf.elffile import ELFFile
from capstone import *

libcccbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so'

with open(libcccbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

start = 0x378e0
code = text_data[start - text_base : start - text_base + 64]
print("Disassembly around 0x378fc:")
for insn in md.disasm(code, start):
    print(f"0x{insn.address:05x}: {insn.mnemonic:8s} {insn.op_str}")


