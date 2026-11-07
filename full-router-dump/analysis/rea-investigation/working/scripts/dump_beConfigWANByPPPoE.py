from elftools.elf.elffile import ELFFile
from capstone import *

libbe_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libbemodules.so'
with open(libbe_path, 'rb') as fp:
    elf = ELFFile(fp)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    rodata_sec = elf.get_section_by_name('.rodata')
    rodata_data = rodata_sec.data()
    rodata_base = rodata_sec['sh_addr']
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s['st_value']: s.name for s in dynsym.iter_symbols() if s['st_value'] != 0}
    rel_plt = elf.get_section_by_name('.rela.plt')
    plt_sec = elf.get_section_by_name('.plt')
    plt_base = plt_sec['sh_addr']
    plt_entries = {}
    if rel_plt:
        for idx, rel in enumerate(rel_plt.iter_relocations()):
            sym = dynsym.get_symbol(rel['r_info_sym'])
            entry_addr = plt_base + 0x20 + idx * 0x10
            plt_entries[entry_addr] = sym.name

def get_str(addr):
    if rodata_base <= addr < rodata_base + len(rodata_data):
        offset = addr - rodata_base
        end = rodata_data.find(b'\x00', offset)
        if end != -1:
            try:
                return rodata_data[offset:end].decode('latin1')
            except:
                return str(rodata_data[offset:end])
    return ''

start = 0x664a8
size = 1712
code = text_data[start - text_base : start - text_base + size]
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

lines = []
regs = {}
for insn in md.disasm(code, start):
    target = ''
    if insn.mnemonic in ['bl', 'b']:
        t_addr = insn.operands[0].imm
        target = plt_entries.get(t_addr, syms.get(t_addr, f'0x{t_addr:x}'))
    elif insn.mnemonic == 'adrp':
        regs[insn.operands[0].reg] = insn.operands[1].imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].reg in regs:
            addr = regs[insn.operands[1].reg] + insn.operands[2].imm
            s = get_str(addr)
            if s: target = f'str: "{s}"'

    lines.append(f'{insn.address:06x}: {insn.mnemonic:8s} {insn.op_str:30s} {target}')

with open('full-router-dump/analysis/rea-investigation/working/beConfigWANByPPPoE_disasm.txt', 'w') as out:
    out.write('\n'.join(lines))
print(f'Wrote {len(lines)} instructions to beConfigWANByPPPoE_disasm.txt')

