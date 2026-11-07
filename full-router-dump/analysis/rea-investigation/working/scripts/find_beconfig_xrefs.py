from elftools.elf.elffile import ELFFile
from capstone import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
    elf = ELFFile(f)
    rodata_sec = elf.get_section_by_name('.rodata')
    ro_data = rodata_sec.data()
    ro_addr = rodata_sec['sh_addr']
    
    idx = ro_data.find(b'beConfigWANByPPPoE\x00')
    target_addr = ro_addr + idx
    print(f"String 'beConfigWANByPPPoE' at 0x{target_addr:x}")
    
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

regs = {}
for insn in md.disasm(text_data, text_base):
    if insn.mnemonic == 'adrp':
        regs[insn.operands[0].reg] = insn.operands[1].imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].type == 1 and insn.operands[2].type == 2:
            src = insn.operands[1].reg
            if src in regs:
                tgt = regs[src] + insn.operands[2].imm
                if tgt == target_addr:
                    print(f"  XREF at 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
    elif insn.mnemonic in ['b', 'ret']:
        regs.clear()


