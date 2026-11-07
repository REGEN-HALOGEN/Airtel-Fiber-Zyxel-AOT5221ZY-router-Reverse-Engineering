import capstone
import elftools.elf.elffile as elffile

path = 'full-router-dump/filesystem/rootfs/lib/MSTC/libcmsg.so'
with open(path, 'rb') as f:
    elf = elffile.ELFFile(f)
    symtab = elf.get_section_by_name('.dynsym')
    sym_addr = None
    sym_size = 0
    for sym in symtab.iter_symbols():
        if sym.name == 'cmsgRequestSetIndexedObj':
            sym_addr = sym['st_value']
            sym_size = sym['st_size']
            break
    print(f"cmsgRequestSetIndexedObj at {hex(sym_addr)}, size {sym_size}")
    
    # get section containing sym_addr
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= sym_addr < s['sh_addr'] + s['sh_size']:
            sec = s
            break
    
    data = sec.data()
    offset = sym_addr - sec['sh_addr']
    code = data[offset:offset+sym_size]

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
for insn in cs.disasm(code, sym_addr):
    print(f"  {hex(insn.address)}: {insn.mnemonic} {insn.op_str}")

