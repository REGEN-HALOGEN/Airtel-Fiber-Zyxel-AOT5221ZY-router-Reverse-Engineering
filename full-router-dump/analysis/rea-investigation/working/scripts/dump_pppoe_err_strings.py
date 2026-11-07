import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    
    for str_addr in [0x5ce5, 0x5cff, 0x5d3a]:
        f_off = str_addr - addr
        end = data.find(b'\x00', f_off)
        print(f"0x{str_addr:x}: \"{data[f_off:end].decode('latin1')}\"")

