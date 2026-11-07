import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()
    
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()
    
    print("=== Symbols in libpppoe.so ===")
    for v, n in sorted(syms.items()):
        print(f"  {hex(v)}: {n}")

# Search for strings in rodata of libpppoe.so
import re
strings = re.findall(b'[\x20-\x7e]{3,}', ro_data)
print("=== Strings in rodata of libpppoe.so ===")
for s in strings:
    print(f"  {s.decode('latin1')}")

