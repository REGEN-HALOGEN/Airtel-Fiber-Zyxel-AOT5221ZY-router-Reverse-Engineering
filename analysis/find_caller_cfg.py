from elftools.elf.elffile import ELFFile
from capstone import *

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')
rela = elf.get_section_by_name('.rela.plt')
plt = elf.get_section_by_name('.plt')
plt_addr = plt['sh_addr']

call_addr = None
for i, r in enumerate(rela.iter_relocations()):
    sym = dynsym.get_symbol(r['r_info_sym'])
    if sym.name == 'createWANPPPConnectionCfgFile':
        call_addr = plt_addr + 32 + i * 16
        print(f'PLT 0x{call_addr:x} -> {sym.name}')
        break

text = elf.get_section_by_name('.text')
base = text['sh_addr']
data = text.data()

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

for insn in md.disasm(data, base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            target = insn.operands[0].imm
            if target == call_addr:
                print(f'Call to createWANPPPConnectionCfgFile from 0x{insn.address:x}')
        except:
            pass

