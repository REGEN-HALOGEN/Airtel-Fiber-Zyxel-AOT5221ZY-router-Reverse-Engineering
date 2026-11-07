from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    rela_dyn = elf.get_section_by_name('.rela.dyn')
    for r in rela_dyn.iter_relocations():
        if r['r_addend'] == 0xbed20:
            print(f"R_AARCH64_RELATIVE to 0xbed20 at offset 0x{r['r_offset']:x}")


