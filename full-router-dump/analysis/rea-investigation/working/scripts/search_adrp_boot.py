import elftools.elf.elffile as elffile
import capstone

def search_adrp_target(elf_path, target_addr):
    page = target_addr & ~0xfff
    offset = target_addr & 0xfff
    print(f"Searching {elf_path} for target 0x{target_addr:x} (page 0x{page:x}, offset 0x{offset:x})")
    
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        text = elf.get_section_by_name('.text')
        text_data = text.data()
        text_addr = text['sh_addr']
        
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        prev = None
        for ins in md.disasm(text_data, text_addr):
            if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
                prev = ins
            elif prev and ins.address == prev.address + 4:
                if hex(offset) in ins.op_str:
                    print(f"  Match: 0x{prev.address:x}: {prev.mnemonic} {prev.op_str}; 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
                prev = None
            else:
                prev = None

search_adrp_target('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 0x50d08)
search_adrp_target('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 0x50d08)

