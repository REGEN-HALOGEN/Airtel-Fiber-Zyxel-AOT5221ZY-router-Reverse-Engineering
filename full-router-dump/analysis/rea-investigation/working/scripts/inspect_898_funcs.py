from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so', 'rb') as f:
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = [(s['st_value'], s['st_size'], s.name) for s in dynsym.iter_symbols() if s['st_value'] != 0 and s['st_size'] > 0]
    syms.sort()

addrs = [0x1afbc, 0x1b774, 0x2cc10, 0x378fc, 0x393bc]

for a in addrs:
    fn = "unknown"
    for sa, ss, sn in syms:
        if sa <= a < sa + ss:
            fn = f"{sn} (0x{sa:x})"
            break
    print(f"Address 0x{a:x} is inside {fn}")


