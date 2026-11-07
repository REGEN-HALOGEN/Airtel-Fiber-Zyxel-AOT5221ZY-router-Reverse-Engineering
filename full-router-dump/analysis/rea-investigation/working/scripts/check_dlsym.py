import elftools.elf.elffile as elffile

for elf_path in [
    'full-router-dump/filesystem/rootfs/usr/bin/ccc_be',
    'full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libcmsg.so'
]:
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')
        names = [s.name for s in dynsym.iter_symbols()]
        dlsym_present = 'dlsym' in names
        print(f"{elf_path}: dlsym in dynsym? {dlsym_present}")

