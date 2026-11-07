from elftools.elf.elffile import ELFFile
from capstone import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [(s['st_value'], s['st_size'], s.name) for s in dynsym.iter_symbols() if s['st_value'] != 0 and s['st_size'] > 0]
    syms.sort()

def get_fn(a):
    for sa, ss, sn in syms:
        if sa <= a < sa + ss:
            return f"{sn} (0x{sa:x})"
    return "unknown"

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
target = 0x1baf0

for insn in md.disasm(text_data, text_base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            if insn.operands[0].imm == target:
                print(f"Call to beConfigWANByPPPoE@plt at 0x{insn.address:x} in {get_fn(insn.address)}")
        except:
            pass


