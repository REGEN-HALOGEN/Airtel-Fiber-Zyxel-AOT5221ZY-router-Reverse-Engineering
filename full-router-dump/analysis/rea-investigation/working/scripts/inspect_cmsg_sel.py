import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/lib/MSTC/libcmsg.so'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    symtab = elf.get_section_by_name('.dynsym')
    sym_addr = None
    sym_size = 0
    for sym in symtab.iter_symbols():
        if sym.name == 'cmsgRequestSel':
            sym_addr = sym['st_value']
            sym_size = sym['st_size']
            break
    print(f"cmsgRequestSel at {hex(sym_addr)}, size {sym_size}")
    
    text = elf.get_section_by_name('.text')
    text_addr = text['sh_addr']
    text_data = text.data()

offset = sym_addr - text_addr
code = text_data[offset:offset+sym_size]
cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
for insn in cs.disasm(code, sym_addr):
    print(f"  {hex(insn.address)}: {insn.mnemonic} {insn.op_str}")

