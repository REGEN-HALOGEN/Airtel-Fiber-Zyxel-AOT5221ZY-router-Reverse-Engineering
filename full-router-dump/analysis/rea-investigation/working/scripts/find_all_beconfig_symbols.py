import os
from elftools.elf.elffile import ELFFile

rootfs = r'full-router-dump\filesystem\rootfs'
pattern = 'beConfigWANByPPPoE'

for root, dirs, files in os.walk(rootfs):
    for f in files:
        p = os.path.join(root, f)
        try:
            with open(p, 'rb') as fp:
                elf = ELFFile(fp)
                dynsym = elf.get_section_by_name('.dynsym')
                if dynsym:
                    for s in dynsym.iter_symbols():
                        if s.name == pattern:
                            print(f"{p}: symbol '{s.name}' found (value=0x{s['st_value']:x}, shndx={s['st_shndx']})")
        except:
            pass


