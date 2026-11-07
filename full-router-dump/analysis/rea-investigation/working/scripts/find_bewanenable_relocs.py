from elftools.elf.elffile import ELFFile

binaries = [
    r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so',
    r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so',
    r'full-router-dump\filesystem\rootfs\usr\bin\ccc_be'
]

for b in binaries:
    with open(b, 'rb') as f:
        elf = ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        syms = [s.name for s in dynsym.iter_symbols()] if dynsym else []
        for sec_name in ['.rela.dyn', '.rela.plt']:
            sec = elf.get_section_by_name(sec_name)
            if sec:
                for r in sec.iter_relocations():
                    sym_idx = r['r_info_sym']
                    if sym_idx < len(syms) and syms[sym_idx] == 'beWanEnablePPPv4Client':
                        print(f"Reloc to beWanEnablePPPv4Client in {b} ({sec_name}) at 0x{r['r_offset']:x}")


