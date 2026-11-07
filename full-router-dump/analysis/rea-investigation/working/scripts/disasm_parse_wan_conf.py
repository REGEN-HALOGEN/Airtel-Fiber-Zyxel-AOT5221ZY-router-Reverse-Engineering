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
    
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [s.name for s in dynsym.iter_symbols()]
    plt_map = {}
    for i, r in enumerate(rela_plt.iter_relocations()):
        sym_idx = r['r_info_sym']
        plt_entry = plt_base + 0x20 + i * 0x10
        plt_map[plt_entry] = syms[sym_idx]

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

start = 0x658b4
size = 600
code = text_data[start - text_base : start - text_base + size]

regs = {}
print("Disassembly of parse_wan_conf (0x658b4):")
for insn in md.disasm(code, start):
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
    elif insn.mnemonic == 'bl':
        target = insn.operands[0].imm
        if target in plt_map:
            comment = f" // <{plt_map[target]}@plt>"
    elif insn.mnemonic in ['b', 'ret']:
        regs.clear()
        
    print(f"0x{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str:32s} {comment}")


