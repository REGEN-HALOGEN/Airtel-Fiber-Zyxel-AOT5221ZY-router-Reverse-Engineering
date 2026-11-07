import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/usr/bin/ccc_be'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    symtab = elf.get_section_by_name('.dynsym')
    
    # Check imports and functions
    for sym in symtab.iter_symbols():
        if any(k in sym.name for k in ['cmsg', 'Rdm', 'Action', 'Index', 'Add']):
            print(f"  {hex(sym['st_value'])}: {sym.name}")

