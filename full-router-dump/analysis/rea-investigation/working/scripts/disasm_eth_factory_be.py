import elftools.elf.elffile as elffile
import capstone

with open('full-router-dump/filesystem/rootfs/usr/bin/ccc_be', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()
    
    # We want to find function prologue before 0x414b9c
    # In AArch64, function prologues commonly look like `stp x29, x30, [sp, -N]!`
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    
    # Let's search backwards from 0x414b9c
    prologue_addr = None
    for a in range(0x414b9c, 0x414000, -4):
        offset = a - text_addr
        code = text_data[offset:offset+4]
        for ins in md.disasm(code, a):
            if ins.mnemonic == 'stp' and 'x29, x30, [sp' in ins.op_str:
                prologue_addr = a
                break
        if prologue_addr:
            break
            
    print(f"Function prologue found at 0x{prologue_addr:x}")
    
    # Disassemble from prologue for 200 instructions
    start_offset = prologue_addr - text_addr
    code = text_data[start_offset:start_offset+800]
    for ins in md.disasm(code, prologue_addr):
        comment = ""
        if ins.mnemonic in ['bl', 'b']:
            try:
                dest = int(ins.op_str.replace('#', ''), 16)
                comment = f" ; target 0x{dest:x}"
            except:
                pass
        print(f"0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str:<32}{comment}")
        if ins.mnemonic == 'ret' and ins.address > 0x414c50:
            print("--- RET ---")
            break

