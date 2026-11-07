from gen_disasm import analyze_func

libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'
analyze_func(libbemodules, 'beWanDoLayer3InterfaceAction_start', 0x6bf78, 0x6c400 - 0x6bf78,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\layer3_start.txt')

