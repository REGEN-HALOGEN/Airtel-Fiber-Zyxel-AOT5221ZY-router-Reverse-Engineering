import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/bin/smuxctl', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    print("smuxctl rodata strings:")
    idx = 0
    while idx < len(data):
        end = data.find(b'\x00', idx)
        if end == -1:
            break
        s = data[idx:end].decode('latin1', 'replace')
        if len(s) > 3:
            print(f"  0x{addr+idx:x}: {s}")
        idx = end + 1

