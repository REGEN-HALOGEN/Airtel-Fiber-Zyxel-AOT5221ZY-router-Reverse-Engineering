import elftools.elf.elffile as elffile
import capstone

for path in [
    'full-router-dump/filesystem/rootfs/lib/MSTC/libpppoe.so',
    'full-router-dump/filesystem/rootfs/bin/pppd'
]:
    with open(path, 'rb') as f:
        elf = elffile.ELFFile(f)
        text = elf.get_section_by_name('.text')
        if not text:
            continue
        text_data = text.data()
        text_addr = text['sh_addr']
        
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        for ins in md.disasm(text_data, text_addr):
            if '8933' in ins.op_str:
                print(f"Found SIOCGIFINDEX (0x8933) in {path} at 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")

