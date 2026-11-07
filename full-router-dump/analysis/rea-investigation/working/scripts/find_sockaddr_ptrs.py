import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    for s in elf.iter_sections():
        data = s.data()
        for off in range(0, len(data)-7, 8):
            val = struct.unpack('<Q', data[off:off+8])[0]
            if val == 0x4d10:
                print(f"Pointer to get_sockaddr_ll in {s.name} at 0x{s['sh_addr'] + off:x}")

