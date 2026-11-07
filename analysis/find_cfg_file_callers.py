from elftools.elf.elffile import ELFFile
from capstone import *

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
text = elf.get_section_by_name('.text')
base = text['sh_addr']
data = text.data()

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

for insn in md.disasm(data, base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            target = insn.operands[0].imm
            if target == 0x6a7c0: # createWANPPPConnectionCfgFile
                print(f'Call to createWANPPPConnectionCfgFile from 0x{insn.address:x}')
        except:
            pass

