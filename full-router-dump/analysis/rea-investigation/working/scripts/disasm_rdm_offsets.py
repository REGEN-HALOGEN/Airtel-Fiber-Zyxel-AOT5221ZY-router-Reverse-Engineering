from elftools.elf.elffile import ELFFile
from capstone import *

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

for addr, name in [(0x0e9dc, "rdmGetPtrOffset"), (0x11728, "cccRdmGetOffsetByOID"), (0x142c4, "cccRdmGetParameterNamePtr")]:
    print(f"\n=== {name} ===")
    code = text_data[addr - text_base : addr - text_base + 64]
    for insn in md.disasm(code, addr):
        print(f"0x{insn.address:05x}: {insn.mnemonic:8s} {insn.op_str}")


