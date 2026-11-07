import os
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

targets = {
    0x4945c: "CheckAndRestartPPP",
    0x49784: "wrapperDoPPP"
}

callers = []

for insn in md.disasm(text_data, text_base):
    if insn.mnemonic in ['bl', 'b']:
        try:
            target = insn.operands[0].imm
            if target in targets:
                fn = get_func_name(insn.address)
                callers.append((insn.address, target, targets[target], fn))
        except:
            pass

print(f"Found {len(callers)} direct callers:")
for addr, target, name, fn in callers:
    print(f"  At 0x{addr:x} calls {name} (0x{target:x}) from inside {fn}")

# Also check if their function pointers are stored in any tables (.data, .rodata, .data.rel.ro)
print("\n--- Checking Function Pointer References ---")
with open(libcmd_path, 'rb') as f:
    full_data = f.read()

import struct
for target, name in targets.items():
    pattern = struct.pack('<Q', target)
    pos = 0
    while True:
        idx = full_data.find(pattern, pos)
        if idx == -1: break
        print(f"  Pointer to {name} (0x{target:x}) found at file offset 0x{idx:x}")
        pos = idx + 8


