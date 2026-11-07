from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\librdm.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = []
    for s in dynsym.iter_symbols():
        if s['st_info']['type'] == 'STT_FUNC' and s['st_size'] > 0:
            syms.append((s['st_value'], s['st_size'], s.name))
    syms.sort()

print(f"Exported functions in librdm.so ({len(syms)} total):")
for addr, size, name in syms:
    if any(k in name.lower() for k in ['param', 'obj', 'get', 'offset', 'value', 'struct']):
        print(f"  0x{addr:05x} (size {size:4d}): {name}")


