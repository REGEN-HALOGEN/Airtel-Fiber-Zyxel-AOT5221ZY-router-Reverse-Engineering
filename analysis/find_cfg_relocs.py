from elftools.elf.elffile import ELFFile

for fname in ['libbemodules.so', 'libcccbe.so', 'ccc_be']:
    fpath = r'C:\Users\REGEN\AirtelModemRev\files\\' + fname
    elf = ELFFile(open(fpath, 'rb'))
    dynsym = elf.get_section_by_name('.dynsym')
    sym_idx = {}
    for idx, sym in enumerate(dynsym.iter_symbols()):
        if 'createWANPPPConnectionCfgFile' in sym.name:
            sym_idx[idx] = sym.name

    for rsec_name in ['.rela.dyn', '.rela.plt']:
        rsec = elf.get_section_by_name(rsec_name)
        if rsec:
            for r in rsec.iter_relocations():
                s_idx = r['r_info_sym']
                if s_idx in sym_idx:
                    print(f'{fname} {rsec_name} offset=0x{r["r_offset"]:x} symbol={sym_idx[s_idx]}')

