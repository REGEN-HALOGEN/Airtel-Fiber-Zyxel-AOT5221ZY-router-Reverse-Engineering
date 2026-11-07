import os
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [s.name for s in dynsym.iter_symbols()]
    
    # Read .rela.plt
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    
    print(f".plt starts at 0x{plt_base:x}")
    # In AArch64 standard PLT, PLT0 is 0x20 bytes, then each PLT entry is 0x10 or 0x20 bytes
    # Let's inspect the relocations
    plt_map = {}
    for i, reloc in enumerate(rela_plt.iter_relocations()):
        sym_idx = reloc['r_info_sym']
        sym_name = syms[sym_idx] if sym_idx < len(syms) else f"sym_{sym_idx}"
        # Typically plt entry i is at plt_base + 0x20 + i * 0x10 or similar
        # But let's check exact PLT entry address if possible, or calculate:
        # On AArch64: PLT0 is 32 bytes (0x20). Each subsequent PLT entry is 16 bytes (0x10).
        entry_addr = plt_base + 0x20 + i * 0x10
        plt_map[entry_addr] = sym_name

    for addr in sorted(plt_map.keys()):
        if addr in [0x44f80, 0x45290, 0x45620, 0x45920, 0x45db0, 0x462c0, 0x44ae0, 0x45090, 0x453a0, 0x44df0, 0x45b90, 0x45bd0]:
            print(f"PLT 0x{addr:x} -> {plt_map[addr]}")

    # Also let's check GOT entries around 0x12afb8
    got_sec = elf.get_section_by_name('.got')
    got_plt_sec = elf.get_section_by_name('.got.plt')
    print(f".got: 0x{got_sec['sh_addr']:x} - 0x{got_sec['sh_addr']+got_sec['sh_size']:x}")
    print(f".got.plt: 0x{got_plt_sec['sh_addr']:x} - 0x{got_plt_sec['sh_addr']+got_plt_sec['sh_size']:x}")
    
    # Check relocations in .rela.dyn for 0x12afb8
    rela_dyn = elf.get_section_by_name('.rela.dyn')
    for reloc in rela_dyn.iter_relocations():
        if reloc['r_offset'] == 0x12afb8:
            sym_idx = reloc['r_info_sym']
            print(f"Reloc at 0x12afb8: sym={syms[sym_idx]}, type={reloc['r_info_type']}")


