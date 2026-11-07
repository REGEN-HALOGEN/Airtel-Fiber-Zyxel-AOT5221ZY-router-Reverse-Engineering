from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    
    # Resolve PLT
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

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

start = 0x66ee4
size = 52
code = text_data[start - text_base : start - text_base + size]

print("==================== beWanEnablePPPv4Client (0x66ee4) ====================")
for insn in md.disasm(code, start):
    comment = ""
    if insn.mnemonic == 'bl':
        target = insn.operands[0].imm
        if target in plt_map:
            comment = f" // <{plt_map[target]}@plt>"
    print(f"0x{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str:32s} {comment}")


