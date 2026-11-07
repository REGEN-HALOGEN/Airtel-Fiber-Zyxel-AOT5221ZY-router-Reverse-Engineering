from elftools.elf.elffile import ELFFile

path = r'c:\Users\REGEN\AirtelModemRev\files\broadband.cgi'
with open(path, 'rb') as f:
    elf = ELFFile(f)
    print('Class:', elf['e_ident']['EI_CLASS'])
    print('Machine:', elf['e_machine'])
    print('Entry:', hex(elf['e_entry']))
    print('Type:', elf['e_type'])
    print()
    print('Sections:')
    for sec in elf.iter_sections():
        addr = sec['sh_addr']
        size = sec['sh_size']
        offset = sec['sh_offset']
        print(f'  {sec.name:20s} addr={hex(addr):12s} size={hex(size):8s} offset={hex(offset):8s}')

    print()
    print('Dynamic symbols:')
    dynsym = elf.get_section_by_name('.dynsym')
    if dynsym:
        for s in dynsym.iter_symbols():
            if s['st_value'] != 0 or s['st_shndx'] != 'SHN_UNDEF':
                val = s['st_value']
                sz = s['st_size']
                bind = s['st_info']['bind']
                typ = s['st_info']['type']
                ndx = s['st_shndx']
                print(f'  {val:08x} {sz:6d} {bind:8s} {typ:8s} {ndx} {s.name}')

