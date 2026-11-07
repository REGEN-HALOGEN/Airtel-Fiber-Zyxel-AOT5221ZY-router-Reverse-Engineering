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
    
    dynsym = elf.get_section_by_name('.dynsym')
    sym_addr = None
    sym_size = 0
    for s in dynsym.iter_symbols():
        if s.name == 'beConfigWANByPPPoE':
            sym_addr = s['st_value']
            sym_size = s['st_size']
            break

print(f"beConfigWANByPPPoE at 0x{sym_addr:x}, size {sym_size}")

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

offset = sym_addr - text_base
code = text_data[offset:offset+min(sym_size, 0x400)]

regs = {}
for insn in md.disasm(code, sym_addr):
    comment = ""
    if insn.mnemonic == 'adrp':
        regs[insn.operands[0].reg] = insn.operands[1].imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].type == 1 and insn.operands[2].type == 2:
            src = insn.operands[1].reg
            if src in regs:
                tgt = regs[src] + insn.operands[2].imm
                s = get_rodata_str(tgt)
                if s: comment = f" // \"{s}\""
    elif insn.mnemonic in ['b', 'ret']:
        regs.clear()
        
    print(f"0x{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str:32s} {comment}")


