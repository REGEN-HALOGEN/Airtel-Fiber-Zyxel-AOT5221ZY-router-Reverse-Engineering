import os
from elftools.elf.elffile import ELFFile

rootfs = r'full-router-dump\filesystem\rootfs'
pattern = 'beConfigWANByPPPoE'

for root, dirs, files in os.walk(rootfs):
    for f in files:
        if f.endswith('.so') or '.' not in f:
            p = os.path.join(root, f)
            try:
                with open(p, 'rb') as fp:
                    elf = ELFFile(fp)
                    for sec_name in ['.dynsym', '.rela.plt', '.rela.dyn']:
                        sec = elf.get_section_by_name(sec_name)
                        if sec and sec_name == '.dynsym':
                            for s in sec.iter_symbols():
                                if s.name == pattern and s['st_shndx'] == 'SHN_UNDEF':
                                    print(f"Undefined reference in {p}")
            except:
                pass


