from elftools.elf.elffile import ELFFile
from capstone import *

def scan_text(bin_path, target_addr):
    print(f"\n--- Scanning {bin_path} for target 0x{target_addr:x} ---")
    with open(bin_path, 'rb') as f:
        elf = ELFFile(f)
        text_sec = elf.get_section_by_name('.text')
        text_data = text_sec.data()
        text_base = text_sec['sh_addr']
        
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        for insn in md.disasm(text_data, text_base):
            if insn.mnemonic in ['bl', 'b']:
                try:
                    if insn.operands[0].imm == target_addr:
                        print(f"  Branch to 0x{target_addr:x} at 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
                except:
                    pass

scan_text(r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so', 0x664a8)
scan_text(r'full-router-dump\filesystem\rootfs\lib\MSTC\libcccbe.so', 0x664a8)


