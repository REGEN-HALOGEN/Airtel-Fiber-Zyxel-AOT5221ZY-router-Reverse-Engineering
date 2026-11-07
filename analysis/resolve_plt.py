from elftools.elf.elffile import ELFFile

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')
rela = elf.get_section_by_name('.rela.plt')
plt = elf.get_section_by_name('.plt')
plt_addr = plt['sh_addr']
plt_size = plt['sh_size']

rel_list = list(rela.iter_relocations())
print(f'PLT addr: 0x{plt_addr:x}, size: {plt_size}, count: {len(rel_list)}')

# AArch64 PLT: first entry is PLT0 (32 bytes), subsequent entries are 16 bytes each
plt_map = {}
for i, r in enumerate(rel_list):
    sym = dynsym.get_symbol(r['r_info_sym'])
    addr = plt_addr + 32 + i * 16
    plt_map[addr] = sym.name

for target in [0x1d1d0, 0x1e9a0, 0x1f1b0, 0x1e4a0, 0x1c180, 0x1d960, 0x1d6b0, 0x1ed70, 0x1be50, 0x1e810, 0x1cc50]:
    name = plt_map.get(target, 'UNKNOWN')
    print(f'PLT 0x{target:x} -> {name}')

