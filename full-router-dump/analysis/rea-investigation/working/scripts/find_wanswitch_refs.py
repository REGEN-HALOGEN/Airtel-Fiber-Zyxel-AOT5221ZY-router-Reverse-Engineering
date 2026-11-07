import re
import capstone
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()
    
    matches = [ro_addr + m.start() for m in re.finditer(b'WANSwitch', ro_data)]
    print("WANSwitch in rodata:", [hex(m) for m in matches])
    
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

curr_adrp = {}
for i, insn in enumerate(insns):
    if insn.mnemonic == 'adrp':
        parts = [p.strip() for p in insn.op_str.split(',')]
        reg = parts[0]
        try:
            curr_adrp[reg] = int(parts[1].replace('#', ''), 16)
        except:
            pass
    elif insn.mnemonic == 'add':
        parts = [p.strip() for p in insn.op_str.split(',')]
        dst = parts[0]
        src = parts[1]
        if src in curr_adrp and len(parts) > 2 and parts[2].startswith('#'):
            imm = int(parts[2].replace('#', ''), 16)
            full_addr = curr_adrp[src] + imm
            if any(abs(full_addr - m) < 8 for m in matches):
                print(f"Ref to WANSwitch at {hex(insn.address)} (addr: {hex(full_addr)})")
                for ctx in insns[max(0, i-5):i+15]:
                    print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")
