from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

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
md.detail = True

regs = {}
for insn in md.disasm(text_data, text_base):
    if insn.mnemonic == 'adrp':
        regs[insn.operands[0].reg] = insn.operands[1].imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].type == ARM64_OP_REG and insn.operands[2].type == ARM64_OP_IMM:
            src = insn.operands[1].reg
            if src in regs:
                tgt = regs[src] + insn.operands[2].imm
                if tgt == 0x664a8:
                    print(f"ADRP+ADD to 0x664a8 at 0x{insn.address:x} in {get_fn(insn.address)}")
    elif insn.mnemonic in ['b', 'ret']:
        regs.clear()


