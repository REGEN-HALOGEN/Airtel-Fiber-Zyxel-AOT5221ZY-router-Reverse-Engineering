import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    f_off = 0x4aee0 - addr
    end = data.find(b'\x00', f_off)
    print("Format string at 0x4aee0:", data[f_off:end].decode('latin1'))

