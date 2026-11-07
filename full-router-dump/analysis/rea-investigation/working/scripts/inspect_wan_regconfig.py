import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    target_sym = None
    for s in (symtab.iter_symbols() if symtab else []):
        if s.name == 'WAN_RegConfigStruct':
            target_sym = s
            break
    if not target_sym and dynsym:
        for s in dynsym.iter_symbols():
            if s.name == 'WAN_RegConfigStruct':
                target_sym = s
                break
                
    if not target_sym:
        print("WAN_RegConfigStruct not found!")
    else:
        addr = target_sym.entry.st_value
        sz = target_sym.entry.st_size
        print(f"WAN_RegConfigStruct at 0x{addr:x}, size {sz} bytes")
        
        # Read relocations for this range
        rela = elf.get_section_by_name('.rela.dyn')
        dynsym_names = [s.name for s in dynsym.iter_symbols()]
        relocs = {}
        if rela:
            for r in rela.iter_relocations():
                if addr <= r['r_offset'] < addr + sz:
                    sname = dynsym_names[r['r_info_sym']] if r['r_info_sym'] < len(dynsym_names) else ""
                    relocs[r['r_offset']] = (r['r_info_type'], sname, r['r_addend'])
                    
        # Also symbols mapping to addresses
        sym_map = {}
        for s in (symtab.iter_symbols() if symtab else []):
            if s.name:
                sym_map[s.entry.st_value] = s.name
        for s in (dynsym.iter_symbols() if dynsym else []):
            if s.name:
                sym_map[s.entry.st_value] = s.name

        # Read section data
        sec = None
        for s in elf.iter_sections():
            if s['sh_addr'] <= addr < s['sh_addr'] + s['sh_size']:
                sec = s
                break
        data = sec.data()[addr - sec['sh_addr'] : addr - sec['sh_addr'] + sz]
        for off in range(0, sz, 8):
            field_addr = addr + off
            val = struct.unpack('<Q', data[off:off+8])[0]
            desc = ""
            if field_addr in relocs:
                rtype, sname, addend = relocs[field_addr]
                desc = f"reloc: {sname} + 0x{addend:x}"
                if addend in sym_map:
                    desc += f" ({sym_map[addend]})"
            elif val in sym_map:
                desc = f"symbol: {sym_map[val]}"
            print(f"  +0x{off:03x} (0x{field_addr:x}): 0x{val:016x}  {desc}")

