from elftools.elf.elffile import ELFFile
import os

files_dir = r'C:\Users\REGEN\AirtelModemRev\files'
for fn in os.listdir(files_dir):
    fp = os.path.join(files_dir, fn)
    if fn.endswith('.so') or fn.endswith('.ko') or fn in ['ccc_be', 'ccc_das', 'diag', 'linkdetection']:
        try:
            elf = ELFFile(open(fp, 'rb'))
            for sname in ['.dynsym', '.symtab']:
                sec = elf.get_section_by_name(sname)
                if sec:
                    for sym in sec.iter_symbols():
                        if 'rtk_wan_port_mapping' in sym.name or 'portWanMap' in sym.name:
                            print(f'{fn} {sname}: {sym.name} @ 0x{sym["st_value"]:x} shndx={sym["st_shndx"]}')
        except Exception as e:
            pass

