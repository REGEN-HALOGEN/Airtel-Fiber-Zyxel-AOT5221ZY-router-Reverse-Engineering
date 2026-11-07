import elftools.elf.elffile as elffile
import capstone

def find_str_refs(elf_path, s_target):
    with open(elf_path, 'rb') as f:
        elf = elffile.ELFFile(f)
        rodata = elf.get_section_by_name('.rodata')
        if not rodata:
            return
        data = rodata.data()
        addr = rodata['sh_addr']
        idx = 0
        matches = []
        while True:
            idx = data.find(s_target, idx)
            if idx == -1:
                break
            str_addr = addr + idx
            end = data.find(b'\x00', idx)
            val = data[idx:end].decode('latin1', 'replace')
            print(f'{elf_path}: found "{val}" at 0x{str_addr:x}')
            matches.append(str_addr)
            idx += 1
        
        # Now find code references in .text
        text = elf.get_section_by_name('.text')
        text_data = text.data()
        text_addr = text['sh_addr']
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        
        # Check adrp references
        for m in matches:
            page = m & ~0xfff
            offset = m & 0xfff
            print(f'Checking refs for 0x{m:x} (page 0x{page:x}, offset 0x{offset:x})')
            prev_adrp = None
            for ins in md.disasm(text_data, text_addr):
                if ins.mnemonic == 'adrp' and hex(page) in ins.op_str:
                    prev_adrp = ins
                elif prev_adrp and ins.address == prev_adrp.address + 4:
                    if hex(offset) in ins.op_str or hex(m) in ins.op_str:
                        print(f'  Match at 0x{prev_adrp.address:x}: {prev_adrp.mnemonic} {prev_adrp.op_str}; 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}')
                    prev_adrp = None
                else:
                    prev_adrp = None

print("=== Checking ccc_be ===")
find_str_refs('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', b'nas0')

print("\n=== Checking libcccbe.so ===")
find_str_refs('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', b'nas0')

