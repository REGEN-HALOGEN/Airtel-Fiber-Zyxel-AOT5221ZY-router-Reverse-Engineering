import capstone
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbemodules.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    rodata = elf.get_section_by_name('.rodata')
    ro_addr = rodata['sh_addr']
    ro_data = rodata.data()
    
    # string at 0xb42c8
    off = 0xb42c8 - ro_addr
    s = ro_data[off:off+64].split(b'\x00')[0]
    print(f"String at 0xb42c8: '{s.decode('latin1')}'")
    
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()
    
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    for i, rel in enumerate(rela_plt.iter_relocations()):
        p_addr = plt['sh_addr'] + 32 + i * 16
        syms[p_addr] = sym_list[rel['r_info_sym']]

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

# Disassemble from 0x50e00 to 0x51000
offset = 0x50e00 - text_addr
code = text_data[offset:offset+0x200]
print("=== Disassembly of 0x50e00 - 0x51000 ===")
for ins in cs.disasm(code, 0x50e00):
    comment = ""
    if ins.mnemonic == 'bl':
        t = int(ins.op_str.replace('#', ''), 16)
        if t in syms:
            comment = f" <{syms[t]}>"
    print(f"  {hex(ins.address)}: {ins.mnemonic} {ins.op_str}{comment}")

