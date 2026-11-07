import os
from gen_disasm import analyze_func

libbemodules = r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so'

analyze_func(libbemodules, 'constructL3WANDevName', 0x698dc, 0x69b30 - 0x698dc,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\constructL3WANDevName.txt')

analyze_func(libbemodules, 'createWANPPPConnectionCfgFile', 0x6a7c0, 0x6a9e0 - 0x6a7c0,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\createWANPPPConnectionCfgFile.txt')

analyze_func(libbemodules, 'OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot', 0x50d08, 0x510bc - 0x50d08,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\OID_InternetGatewayDevice_WANDevice_i_ConfigLoaderFunc_Boot.txt')

