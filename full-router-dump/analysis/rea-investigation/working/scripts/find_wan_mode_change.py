import capstone
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
insns = list(cs.disasm(text_data, text_addr))

target_page = 0xb4000
for i, ins in enumerate(insns):
    if ins.mnemonic == 'adrp' and hex(target_page) in ins.op_str:
        # Check next instruction for add
        next_ins = insns[i+1]
        if next_ins.mnemonic == 'add' and '0x1' in next_ins.op_str:
            print(f"Ref near {hex(ins.address)}: {ins.mnemonic} {ins.op_str}; {next_ins.mnemonic} {next_ins.op_str}")
            for ctx in insns[max(0, i-5):i+20]:
                print(f"  {hex(ctx.address)}: {ctx.mnemonic} {ctx.op_str}")

