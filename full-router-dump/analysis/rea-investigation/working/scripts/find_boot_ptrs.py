import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rela = elf.get_section_by_name('.rela.dyn')
    symtab = elf.get_section_by_name('.symtab')
    dynsym = elf.get_section_by_name('.dynsym')
    
    # Check all relocations with addend == 0x50d08 or pointing to this symbol
    target = 0x50d08
    print("Searching relocations for addend or target 0x50d08:")
    for r in rela.iter_relocations():
        if r['r_addend'] == target:
            print(f"Rela at 0x{r['r_offset']:x}, type {r['r_info_type']}, addend 0x{r['r_addend']:x}")
            
    # Also check if any raw pointer has 0x50d08
    for s in elf.iter_sections():
        data = s.data()
        if len(data) >= 8:
            for off in range(0, len(data)-7, 8):
                val = struct.unpack('<Q', data[off:off+8])[0]
                if val == target:
                    print(f"Raw pointer in section {s.name} at 0x{s['sh_addr'] + off:x}")

