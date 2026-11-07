import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    for ins in md.disasm(text_data, text_addr):
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                if dest == 0x4d10:
                    print(f"Called from 0x{ins.address:x}")
            except:
                pass

