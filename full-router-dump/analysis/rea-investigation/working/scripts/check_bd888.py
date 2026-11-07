from elftools.elf.elffile import ELFFile

with open(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 'rb') as f:
    elf = ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_data = rodata.data()
    ro_addr = rodata['sh_addr']
    
    offset = 0xbd888 - ro_addr
    end = ro_data.find(b'\x00', offset)
    print(f"String at 0xbd888: {ro_data[offset:end].decode('latin1')}")


