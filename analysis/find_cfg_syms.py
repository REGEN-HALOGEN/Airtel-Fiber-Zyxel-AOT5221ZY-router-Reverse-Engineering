from elftools.elf.elffile import ELFFile

targets = ['createWANPPPConnectionCfgFile', 'createWANPPPConnectionCfgFile_wrapper', 'libcccBeWan_createWANPPPConnectionCfgFile_wrapper']

for fname in ['libbemodules.so', 'libcccbe.so', 'ccc_be']:
    fpath = r'C:\Users\REGEN\AirtelModemRev\files\\' + fname
    elf = ELFFile(open(fpath, 'rb'))
    dynsym = elf.get_section_by_name('.dynsym')
    for sym in dynsym.iter_symbols():
        if any(t in sym.name for t in targets):
            print(f'{fname}: dynsym {sym.name} @ 0x{sym["st_value"]:x} type={sym["st_info"]["type"]}')

