from elftools.elf.elffile import ELFFile
from capstone import *

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
dynsym = elf.get_section_by_name('.dynsym')
rela = elf.get_section_by_name('.rela.plt')
plt = elf.get_section_by_name('.plt')
plt_addr = plt['sh_addr']

plt_targets = {}
for i, r in enumerate(rela.iter_relocations()):
    sym = dynsym.get_symbol(r['r_info_sym'])
    call_addr = plt_addr + 32 + i * 16
    if sym.name in ['beConfigWANByPPPoE', 'beWanEnablePPPv4Client', 'pppConfigSet', 'pppConnection', 'setWanIpPppInterfaceName', 'libcccBeWan_eth_Init']:
        plt_targets[call_addr] = sym.name
        print(f'PLT 0x{call_addr:x} -> {sym.name}')

# Now scan .text for calls to these PLT addresses
text = elf.get_section_by_name('.text')
base = text['sh_addr']
data = text.data()

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

for insn in md.disasm(data, base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            target = insn.operands[0].imm
            if target in plt_targets:
                print(f'Call to {plt_targets[target]} from 0x{insn.address:x}')
        except:
            pass

