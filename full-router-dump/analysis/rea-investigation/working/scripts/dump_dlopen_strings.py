import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    data = rodata.data()
    addr = rodata['sh_addr']
    
    offsets = [0xf50, 0xf60, 0xf68, 0xf88, 0xf98, 0xfb0, 0xfc0, 0xfe0]
    for off in offsets:
        str_addr = 0x415000 + off
        f_off = str_addr - addr
        end = data.find(b'\x00', f_off)
        print(f"0x{str_addr:x}: \"{data[f_off:end].decode('latin1', 'replace')}\"")
        
    # Also check what symbols are in the array at 0x42d148 or what string list is there
    # Let's inspect the caller of this entire dlopen loop!
    # Where does this function start?

