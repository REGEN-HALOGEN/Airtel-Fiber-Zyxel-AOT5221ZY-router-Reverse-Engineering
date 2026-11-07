from elftools.elf.elffile import ELFFile

targets = {
    0x664a8: 'beConfigWANByPPPoE',
    0x66ee4: 'beWanEnablePPPv4Client',
    0x65f64: 'pppConfigSet',
    0x973c0: 'pppConnection',
    0x346d0: 'setWanIpPppInterfaceName',
    0x38074: 'libcccBeWan_eth_Init'
}

for fname in ['libbemodules.so', 'libcccbe.so', 'ccc_be']:
    elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\\' + fname, 'rb'))
    dynsym = elf.get_section_by_name('.dynsym')
    sym_idx = {}
    for idx, sym in enumerate(dynsym.iter_symbols()):
        if sym.name in targets.values():
            sym_idx[idx] = sym.name

    for rsec_name in ['.rela.dyn', '.rela.plt']:
        rsec = elf.get_section_by_name(rsec_name)
        if rsec:
            for r in rsec.iter_relocations():
                s_idx = r['r_info_sym']
                if s_idx in sym_idx:
                    print(f'{fname} {rsec_name} offset=0x{r["r_offset"]:x} symbol={sym_idx[s_idx]}')
                if r['r_info_type'] == 1027: # R_AARCH64_RELATIVE
                    addend = r['r_addend']
                    if addend in targets:
                        print(f'{fname} {rsec_name} offset=0x{r["r_offset"]:x} RELATIVE-> {targets[addend]} (0x{addend:x})')

