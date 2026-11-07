from elftools.elf.elffile import ELFFile
from gen_disasm import analyze_func

fpath = r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so'
elf = ELFFile(open(fpath, 'rb'))
dynsym = elf.get_section_by_name('.dynsym')

for sym in dynsym.iter_symbols():
    if 'getWANDeviceObjectRequestedLinkType' in sym.name:
        addr = sym['st_value']
        size = sym['st_size']
        print(f'Found {sym.name} @ 0x{addr:x}, size {size}')
        analyze_func(fpath, sym.name, addr, size, r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\getLinkType.txt')

