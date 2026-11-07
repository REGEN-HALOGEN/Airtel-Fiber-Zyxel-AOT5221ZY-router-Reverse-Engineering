import elftools.elf.elffile as elffile

for path in [
    'full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so',
    'full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so'
]:
    with open(path, 'rb') as f:
        elf = elffile.ELFFile(f)
        rodata = elf.get_section_by_name('.rodata')
        if not rodata:
            continue
        data = rodata.data()
        addr = rodata['sh_addr']
        idx = 0
        while True:
            idx = data.find(b'kill', idx)
            if idx == -1:
                break
            start = data.rfind(b'\x00', 0, idx)
            start = 0 if start == -1 else start + 1
            end = data.find(b'\x00', idx)
            s = data[start:end].decode('latin1', 'replace')
            if 'ppp' in s.lower() or 'nas0' in s.lower() or 'kill' in s.lower():
                print(f"{path} at 0x{addr+start:x}: \"{s}\"")
            idx = end + 1

