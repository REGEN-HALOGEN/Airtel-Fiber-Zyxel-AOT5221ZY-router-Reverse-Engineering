import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    symtab = elf.get_section_by_name('.symtab')
    
    syms = {}
    for s in (symtab.iter_symbols() if symtab else []):
        syms[s.name] = s.entry.st_value
    for s in (dynsym.iter_symbols() if dynsym else []):
        syms[s.name] = s.entry.st_value
        
    print("cccBeRegConfigObj in ccc_be:", hex(syms.get('cccBeRegConfigObj', 0)))
    print("cccBeConfigLoad in ccc_be:", hex(syms.get('cccBeConfigLoad', 0)))
    
    # Check all exported symbols starting with cccBe
    for name, val in sorted(syms.items(), key=lambda x: x[1]):
        if name.startswith('cccBe'):
            print(f"  0x{val:08x}: {name}")

