import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    sym_map = {}
    for s in (symtab.iter_symbols() if symtab else []):
        sym_map[s.entry.st_value] = s.name
    for s in (dynsym.iter_symbols() if dynsym else []):
        sym_map[s.entry.st_value] = s.name

    rela = elf.get_section_by_name('.rela.dyn')
    dynsym_names = [s.name for s in dynsym.iter_symbols()]
    
    # Let's inspect WANConfig_ConfigSettingStruct (at 0xe6790) and neighboring structs
    for r in rela.iter_relocations():
        if 0xe6750 <= r['r_offset'] <= 0xe6850:
            sname = dynsym_names[r['r_info_sym']] if r['r_info_sym'] < len(dynsym_names) else ""
            desc = sym_map.get(r['r_addend'], "")
            print(f"Rela at 0x{r['r_offset']:x}: sym '{sname}', addend 0x{r['r_addend']:x} ({desc})")

