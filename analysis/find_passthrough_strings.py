from elftools.elf.elffile import ELFFile
from capstone import *

elf = ELFFile(open(r'C:\Users\REGEN\AirtelModemRev\files\libcccbe.so', 'rb'))
text = elf.get_section_by_name('.text')
base = text['sh_addr']
tdata = text.data()

rodata = elf.get_section_by_name('.rodata')
rbase = rodata['sh_addr']
rdata = rodata.data()

def get_str(addr):
    if rbase <= addr < rbase + len(rdata):
        off = addr - rbase
        nul = rdata.find(b'\x00', off)
        return rdata[off:nul].decode('latin1', errors='replace')
    return ''

func_addr = 0x373b8
func_size = 2228
sub = tdata[func_addr - base : func_addr - base + func_size]

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

reg_state = {}
for insn in md.disasm(sub, func_addr):
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
            st = get_str(addr)
            if st and len(st) > 3:
                print(f'0x{insn.address:x}: str at 0x{addr:x} -> {repr(st)}')
            if insn.mnemonic == 'add':
                reg_state[dst] = addr

