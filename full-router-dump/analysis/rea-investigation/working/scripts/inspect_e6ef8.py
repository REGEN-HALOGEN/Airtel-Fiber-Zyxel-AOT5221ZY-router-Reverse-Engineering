import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    
    # We need to find the relocations for 0xe6ef8 or read .got / .data
    # In ELF, let's find section containing 0xe6ef8
    for s in elf.iter_sections():
        if s['sh_addr'] <= 0xe6ef8 < s['sh_addr'] + s['sh_size']:
            off = 0xe6ef8 - s['sh_addr']
            data = s.data()[off:off+8]
            val = struct.unpack('<Q', data)[0]
            print(f"Direct value at 0xe6ef8 in {s.name}: 0x{val:x}")
            
    # Check rela.dyn
    rela = elf.get_section_by_name('.rela.dyn')
    dynsym = elf.get_section_by_name('.dynsym')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    for r in rela.iter_relocations():
        if r['r_offset'] == 0xe6ef8:
            sym_name = sym_list[r['r_info_sym']] if r['r_info_sym'] < len(sym_list) else ""
            print(f"Relocation at 0xe6ef8: type {r['r_info_type']}, sym {sym_name}, addend 0x{r['r_addend']:x}")

