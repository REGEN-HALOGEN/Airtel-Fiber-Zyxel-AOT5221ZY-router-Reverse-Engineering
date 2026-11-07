from elftools.elf.elffile import ELFFile
from capstone import *

path = r'c:\Users\REGEN\AirtelModemRev\files\broadband.cgi'
with open(path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    rodata_sec = elf.get_section_by_name('.rodata')
    rodata_data = rodata_sec.data()
    rodata_base = rodata_sec['sh_addr']
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s['st_value']: s.name for s in dynsym.iter_symbols() if s['st_value'] != 0}
    rel_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    plt_entries = {}
    if rel_plt:
        for idx, rel in enumerate(rel_plt.iter_relocations()):
            sym = dynsym.get_symbol(rel['r_info_sym'])
            entry_addr = plt_base + 0x20 + idx * 0x10
            plt_entries[entry_addr] = sym.name

    print('=== PLT ENTRIES ===')
    for addr in sorted(plt_entries.keys()):
        print(f'  0x{addr:06x}: {plt_entries[addr]}')

