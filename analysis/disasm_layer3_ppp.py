from gen_disasm import analyze_func

libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'

# Let's analyze 0x6c780 to 0x6c900
analyze_func(libbemodules, 'beWanDoLayer3InterfaceAction_PPP', 0x6c780, 0x180,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\beWanDoLayer3InterfaceAction_PPP.txt')

