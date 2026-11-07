import capstone
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libcccbe.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()
    
    # get symbol names
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.entry.st_value: s.name for s in dynsym.iter_symbols()}
    rela_plt = elf.get_section_by_name('.rela.plt')
    plt = elf.get_section_by_name('.plt')
    sym_list = [s.name for s in dynsym.iter_symbols()]
    for i, rel in enumerate(rela_plt.iter_relocations()):
        p_addr = plt['sh_addr'] + 32 + i * 16
        syms[p_addr] = sym_list[rel['r_info_sym']]

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

def disasm_func(addr, size, name):
    print(f"\n=== Function {name} at {hex(addr)} (size {size}) ===")
    offset = addr - text_addr
    code = text_data[offset:offset+size]
    for ins in cs.disasm(code, addr):
        comment = ""
        if ins.mnemonic == 'bl':
            t = int(ins.op_str.replace('#', ''), 16)
            if t in syms:
                comment = f" <{syms[t]}>"
        print(f"  {hex(ins.address)}: {ins.mnemonic} {ins.op_str}{comment}")

disasm_func(0x346d0, 548, "setWanIpPppInterfaceName")
disasm_func(0x348f4, 140, "libccc_executePPPv4Client")
disasm_func(0x373a4, 8, "libcccBeWan_createWANPPPConnectionCfgFile_wrapper")

