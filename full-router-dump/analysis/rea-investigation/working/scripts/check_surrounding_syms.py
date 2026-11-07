from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [(s['st_value'], s['st_size'], s.name) for s in dynsym.iter_symbols() if s['st_value'] != 0 and s['st_size'] > 0]
    syms.sort()

target = 0x66ee4
for i, (addr, size, name) in enumerate(syms):
    if addr == target:
        for j in range(max(0, i-5), min(len(syms), i+6)):
            print(f"0x{syms[j][0]:x} (size {syms[j][1]:4d}): {syms[j][2]}")
        break


