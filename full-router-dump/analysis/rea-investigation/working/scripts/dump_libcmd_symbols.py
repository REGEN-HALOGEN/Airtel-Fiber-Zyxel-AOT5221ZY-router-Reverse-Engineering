import os
from elftools.elf.elffile import ELFFile

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [s.name for s in dynsym.iter_symbols()]
    
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    
    plt_map = {}
    for i, reloc in enumerate(rela_plt.iter_relocations()):
        sym_idx = reloc['r_info_sym']
        sym_name = syms[sym_idx] if sym_idx < len(syms) else f"sym_{sym_idx}"
        entry_addr = plt_base + 0x20 + i * 0x10
        plt_map[entry_addr] = sym_name

    rela_dyn = elf.get_section_by_name('.rela.dyn')
    got_map = {}
    for reloc in rela_dyn.iter_relocations():
        sym_idx = reloc['r_info_sym']
        if sym_idx < len(syms):
            got_map[reloc['r_offset']] = syms[sym_idx]

print(f"Total PLT entries: {len(plt_map)}")
print(f"Total GOT relocs: {len(got_map)}")

# Save to a python dict file or json for disassembler to import
import json
with open(r'full-router-dump\analysis\rea-investigation\working\scripts\libcmd_symbols.json', 'w') as out:
    json.dump({'plt': {str(k): v for k, v in plt_map.items()}, 'got': {str(k): v for k, v in got_map.items()}}, out, indent=2)

print("Saved symbols to libcmd_symbols.json")


