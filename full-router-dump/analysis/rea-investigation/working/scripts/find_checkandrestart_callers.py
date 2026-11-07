from elftools.elf.elffile import ELFFile
from capstone import *

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_base = text_sec['sh_addr']
    
    dynsym = elf.get_section_by_name('.dynsym')
    syms = []
    for s in dynsym.iter_symbols():
        if s['st_info']['type'] == 'STT_FUNC' and s['st_size'] > 0:
            syms.append((s['st_value'], s['st_size'], s.name))
    syms.sort()

def get_func_name(addr):
    for s_addr, s_size, s_name in syms:
        if s_addr <= addr < s_addr + s_size:
            return f"{s_name} (0x{s_addr:x})"
    return "unknown"

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

target = 0x461b0
callers = []

for insn in md.disasm(text_data, text_base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            if insn.operands[0].imm == target:
                fn = get_func_name(insn.address)
                callers.append((insn.address, fn))
        except:
            pass

print(f"Found {len(callers)} callers of CheckAndRestartPPP@plt (0x461b0):")
for addr, fn in callers:
    print(f"  At 0x{addr:x} inside {fn}")


