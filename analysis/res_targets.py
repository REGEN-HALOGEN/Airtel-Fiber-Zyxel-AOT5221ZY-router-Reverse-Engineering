from elftools.elf.elffile import ELFFile

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')
rela = elf.get_section_by_name('.rela.plt')
plt = elf.get_section_by_name('.plt')
plt_addr = plt['sh_addr']

plt_map = {}
for i, r in enumerate(rela.iter_relocations()):
    sym = dynsym.get_symbol(r['r_info_sym'])
    call_addr = plt_addr + 32 + i * 16
    plt_map[call_addr] = sym.name

targets = [0x1de40, 0x1d460, 0x1d340, 0x1e230, 0x1f2f0, 0x1df40, 0x1dae0, 0x1bc10, 0x1dad0, 0x1efd0, 0x1cbd0, 0x1f150]
for a in targets:
    print(f'0x{a:x} -> {plt_map.get(a, "unknown")}')

