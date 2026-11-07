from elftools.elf.elffile import ELFFile
from capstone import *

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libbemodules.so', 'rb'))
text = elf.get_section_by_name('.text')
base = text['sh_addr']
tdata = text.data()

# 0xbd4a0 and 0xbdc60
targets = [0xbd4a0, 0xbdc60, 0xbd4a8]

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

reg_state = {}
for insn in md.disasm(tdata, base):
    if insn.mnemonic == 'adrp':
        reg = insn.op_str.split(',')[0].strip()
        reg_state[reg] = insn.operands[1].imm
    elif insn.mnemonic in ['add', 'ldr']:
        parts = [p.strip() for p in insn.op_str.split(',')]
        dst = parts[0]
        if len(parts) >= 2 and parts[1] in reg_state:
            base_val = reg_state[parts[1]]
            off = 0
            if len(parts) >= 3:
                try:
                    off = int(parts[2].strip(' []#'), 0)
                except:
                    off = 0
            addr = base_val + off
            if addr in targets:
                print(f'Reference to 0x{addr:x} at 0x{insn.address:x}')
            if insn.mnemonic == 'add':
                reg_state[dst] = addr

