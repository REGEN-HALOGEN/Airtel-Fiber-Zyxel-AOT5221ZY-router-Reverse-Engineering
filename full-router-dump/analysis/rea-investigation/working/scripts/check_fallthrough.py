from elftools.elf.elffile import ELFFile
from capstone import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

start = 0x66460
size = 80
code = text_data[start - text_base : start - text_base + size]

print("Disassembly around 0x66460 - 0x664b0:")
for insn in md.disasm(code, start):
    print(f"0x{insn.address:05x}: {insn.mnemonic:8s} {insn.op_str}")


