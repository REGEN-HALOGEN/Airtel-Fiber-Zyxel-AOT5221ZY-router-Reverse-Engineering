from elftools.elf.elffile import ELFFile

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')
rela = elf.get_section_by_name('.rela.plt')
plt = elf.get_section_by_name('.plt')
plt_addr = plt['sh_addr']

plt_map = {}
for i, r in enumerate(rela.iter_relocations()):
    sym = dynsym.get_symbol(r['r_info_sym'])
    call_addr = plt_addr + 32 + i * 16
    plt_map[call_addr] = sym.name

targets = [0x19a20, 0x195e0, 0x197d0, 0x19d50, 0x1a110, 0x19890, 0x1a140, 0x198a0, 0x19ad0]
for a in targets:
    print(f'0x{a:x} -> {plt_map.get(a, "unknown")}')

