from gen_disasm import analyze_func

libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'
analyze_func(libbemodules, 'OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_L3ConfigInit', 0x4f440, 0x4fcb0 - 0x4f440,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\L3ConfigInit.txt')

