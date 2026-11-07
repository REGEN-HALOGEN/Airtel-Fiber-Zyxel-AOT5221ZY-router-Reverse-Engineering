from gen_disasm import analyze_func

libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'
analyze_func(libbemodules, 'beWanDoLayer3InterfaceAction_mid', 0x6c300, 0x6c780 - 0x6c300,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\layer3_mid.txt')

