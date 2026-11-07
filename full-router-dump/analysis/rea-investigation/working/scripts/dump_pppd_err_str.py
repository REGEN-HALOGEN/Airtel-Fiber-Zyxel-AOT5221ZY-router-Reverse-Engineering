import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/bin/pppd', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    for s_addr in [0x42b1ed, 0x42b26d]:
        off = s_addr - addr
        end = data.find(b'\x00', off)
        print(f"0x{s_addr:x}: \"{data[off:end].decode('latin1')}\"")

