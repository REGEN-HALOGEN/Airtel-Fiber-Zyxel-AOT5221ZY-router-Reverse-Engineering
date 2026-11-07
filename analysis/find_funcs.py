from elftools.elf.elffile import ELFFile

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')

syms = []
for s in dynsym.iter_symbols():
    if s['st_info']['type'] == 'STT_FUNC' and s['st_shndx'] != 'SHN_UNDEF':
        syms.append((s['st_value'], s['st_size'], s.name))

syms.sort()

call_sites = [
    (0x50ed4, 'libcccBeWan_eth_Init'),
    (0x68d14, 'pppConfigSet'),
    (0x69980, 'setWanIpPppInterfaceName_1'),
    (0x69aa0, 'setWanIpPppInterfaceName_2'),
    (0x6a8b8, 'beConfigWANByPPPoE'),
    (0x6c834, 'beWanEnablePPPv4Client'),
    (0x9a2dc, 'pppConnection')
]

for addr, target_name in call_sites:
    found = False
    for val, size, name in syms:
        if val <= addr < val + size:
            print(f'Call to {target_name} at 0x{addr:x} is inside function {name} (0x{val:x} - 0x{val+size:x})')
            found = True
            break
    if not found:
        # Find closest preceding symbol
        prev = [(v, s, n) for v, s, n in syms if v <= addr]
        if prev:
            v, s, n = prev[-1]
            print(f'Call to {target_name} at 0x{addr:x} is after {n} (0x{v:x}, size {s})')
        else:
            print(f'Call to {target_name} at 0x{addr:x} has no preceding symbol')

