import os
import elftools.elf.elffile as elffile

target = 'cccBeRegConfigObj'
for root, dirs, files in os.walk('full-router-dump/filesystem/rootfs/lib'):
    for f in files:
        if f.endswith('.so') or '.so.' in f:
            p = os.path.join(root, f)
            try:
                with open(p, 'rb') as fp:
                    elf = elffile.ELFFile(fp)
                    dynsym = elf.get_section_by_name('.dynsym')
                    if dynsym:
                        for s in dynsym.iter_symbols():
                            if s.name == target and s['st_shndx'] != 'SHN_UNDEF':
                                print(f"DEFINED in {p}: value 0x{s.entry.st_value:x}")
            except:
                pass

