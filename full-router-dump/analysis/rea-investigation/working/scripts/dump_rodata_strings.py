with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    data = f.read()

import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()

addrs = [0x4aee0, 0x40ad8, 0x4aeb0, 0x4aea8, 0x4d990, 0x4c160, 0x4aeb8, 0x454f0]
for a in addrs:
    if ro_addr <= a < ro_addr + len(ro_data):
        off = a - ro_addr
        s = ro_data[off:off+100].split(b'\x00')[0]
        print(f"{hex(a)}: {s.decode('latin1', errors='replace')}")
    else:
        print(f"{hex(a)}: NOT in rodata (rodata is {hex(ro_addr)} to {hex(ro_addr+len(ro_data))})")

