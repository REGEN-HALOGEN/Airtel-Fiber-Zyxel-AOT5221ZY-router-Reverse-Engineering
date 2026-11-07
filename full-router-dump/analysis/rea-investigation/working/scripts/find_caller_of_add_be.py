import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/usr/bin/ccc_be'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_data = text.data()
    text_addr = text['sh_addr']

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

# Find references/calls to 0x415860
for i, insn in enumerate(insns):
    if insn.mnemonic in ['bl', 'b'] and insn.op_str.strip() == '#0x415860':
        print(f"Call to 0x415860 from {hex(insn.address)}")
        start = max(0, i - 20)
        end = min(len(insns), i + 15)
        for ctx in insns[start:end]:
            print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")

