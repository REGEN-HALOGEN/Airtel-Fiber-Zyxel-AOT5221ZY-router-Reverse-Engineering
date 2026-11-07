from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'

with open(libbe_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    
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

    local_syms = {s['st_value']: s.name for s in dynsym.iter_symbols() if s['st_value'] != 0}

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

start = 0x65f64
size = 1348
code = text_data[start - text_base : start - text_base + size]

print(f"=== Calls inside pppConfigSet (0x{start:x} - 0x{start+size:x}) ===")
for insn in md.disasm(code, start):
    if insn.mnemonic in ['bl', 'b']:
        try:
            target = insn.operands[0].imm
            callee = plt_map.get(target, local_syms.get(target, f"0x{target:x}"))
            if insn.mnemonic == 'bl' or target < start or target >= start + size:
                print(f"  0x{insn.address:05x}: {insn.mnemonic:4s} -> {callee}")
        except:
            pass


