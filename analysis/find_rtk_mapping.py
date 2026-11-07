from elftools.elf.elffile import ELFFile
from gen_disasm import analyze_func

librtk = r'C:\Users\REGEN\AirtelModemRev\files\librtk.so'
elf = ELFFile(open(librtk, 'rb'))
symtab = elf.get_section_by_name('.symtab')

for sym in symtab.iter_symbols():
    if sym.name == 'rtk_wan_port_mapping':
        print(f'rtk_wan_port_mapping @ 0x{sym["st_value"]:x}, size {sym["st_size"]}')
        analyze_func(librtk, 'rtk_wan_port_mapping', sym['st_value'], sym['st_size'],
                     r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\rtk_wan_port_mapping.txt')
        break

