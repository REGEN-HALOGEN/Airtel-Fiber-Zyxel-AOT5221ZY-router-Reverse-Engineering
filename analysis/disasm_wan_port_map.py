from gen_disasm import analyze_func

libcccbe = r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so'
analyze_func(libcccbe, 'rtk_wan_port_mapping', 0x37c84, 0x38074 - 0x37c84,
             r'C:\Users\REGEN\AirtelModemRev\analysis\disasm\rtk_wan_port_mapping.txt')

