import elftools.elf.elffile as elffile
import capstone

# Let's inspect libbe.so: 0x1140 (cccBeRegConfigObj)
with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    start_addr = 0x1140
    off = start_addr - text_addr
    print("=== cccBeRegConfigObj in libbe.so ===")
    for ins in md.disasm(text_data[off:off+0x100], start_addr):
        print(f"0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str:<32}")
        if ins.mnemonic == 'ret':
            break

