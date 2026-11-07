import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    
    for offset in range(0xd80, 0xe20, 8):
        file_off = (0x419000 + offset) - addr
        end = data.find(b'\x00', file_off)
        s = data[file_off:end].decode('latin1', 'replace')
        print(f"0x{0x419000 + offset:x}: \"{s}\"")

