from elftools.elf.elffile import ELFFile

targets = ['beConfigWANByPPPoE', 'createLayer3Interface', 'beWanEnablePPPv4Client', 'libccc_executePPPv4Client']

binaries = [
    r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so',
    r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so',
    r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so',
    r'full-router-dump\filesystem\rootfs\usr\bin\ccc_be'
]

for b in binaries:
    print(f"\n--- Checking {b} ---")
    with open(b, 'rb') as f:
        elf = ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        if dynsym:
            for s in dynsym.iter_symbols():
                if s.name in targets:
                    print(f"  {s.name:30s} : value=0x{s['st_value']:x}, size={s['st_size']}, type={s['st_info']['type']}")


