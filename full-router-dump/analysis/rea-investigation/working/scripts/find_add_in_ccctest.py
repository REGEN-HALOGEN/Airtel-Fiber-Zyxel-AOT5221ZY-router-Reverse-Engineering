import capstone
import elftools.elf.elffile as elffile
import re

with open('full-router-dump/filesystem/rootfs/usr/bin/ccctest', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_data = rodata.data()
    ro_addr = rodata['sh_addr']
    
    add_addrs = [ro_addr + m.start() for m in re.finditer(b'ADD\x00', ro_data)]
    print("ADD string addrs:", [hex(a) for a in add_addrs])
    
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

curr_adrp = {}
for i, insn in enumerate(insns):
    if insn.mnemonic == 'adrp':
        parts = [p.strip() for p in insn.op_str.split(',')]
        reg = parts[0]
        imm_str = parts[1].replace('#', '')
        curr_adrp[reg] = int(imm_str, 16)
    elif insn.mnemonic == 'add':
        parts = [p.strip() for p in insn.op_str.split(',')]
        dst = parts[0]
        src = parts[1]
        if src in curr_adrp and len(parts) > 2:
            imm_str = parts[2].replace('#', '')
            imm = int(imm_str, 16)
            full_addr = curr_adrp[src] + imm
            if full_addr in add_addrs:
                print(f"Match at {hex(insn.address)}: computes {hex(full_addr)} ('ADD')")
                start = max(0, i - 10)
                end = min(len(insns), i + 35)
                for ctx in insns[start:end]:
                    print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")
