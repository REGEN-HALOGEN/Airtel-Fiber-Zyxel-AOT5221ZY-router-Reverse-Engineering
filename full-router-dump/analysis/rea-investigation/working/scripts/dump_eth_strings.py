import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()

addrs = [0x4c1e0, 0x4c268, 0x4c2a0, 0x4c2d8, 0x4c380]
for a in addrs:
    off = a - ro_addr
    s = ro_data[off:off+100].split(b'\x00')[0]
    print(f"{hex(a)}: {s.decode('latin1', errors='replace')}")

