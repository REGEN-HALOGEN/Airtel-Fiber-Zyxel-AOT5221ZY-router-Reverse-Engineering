import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/usr/bin/ccc_be'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
# Disassemble from 0x414800 to 0x415600
offset_start = 0x414800 - text_addr
offset_end = 0x415600 - text_addr
code = text_data[offset_start:offset_end]

for insn in cs.disasm(code, 0x414800):
    print(f"  {hex(insn.address)}: {insn.mnemonic} {insn.op_str}")

