import os
from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.arm64 import *

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    text_sec = elf.get_section_by_name('.text')
    text_data = text_sec.data()
    text_addr = text_sec['sh_addr']
    
    rodata_sec = elf.get_section_by_name('.rodata')
    rodata_data = rodata_sec.data()
    rodata_addr = rodata_sec['sh_addr']
    rodata_offset = rodata_sec['sh_offset']
    
    # Also load symbol table if available
    symtab = elf.get_section_by_name('.dynsym')
    symbols = []
    if symtab:
        for sym in symtab.iter_symbols():
            if sym['st_value'] != 0 and sym['st_info']['type'] in ['STT_FUNC', 'STT_NOTYPE']:
                symbols.append((sym['st_value'], sym['st_size'], sym.name))
    symbols.sort()

# Dump string block around 0xcad00 - 0xcb100
print("--- Rodata Strings 0xcad00 - 0xcb100 ---")
with open(libcmd_path, 'rb') as f:
    f.seek(0xcad00)
    chunk = f.read(0x500)

pos = 0xcad00
while pos < 0xcad00 + len(chunk):
    # find next null
    end = chunk.find(b'\x00', pos - 0xcad00)
    if end == -1:
        break
    s = chunk[pos - 0xcad00:end]
    if len(s) > 0 and all(32 <= b <= 126 or b in [10, 13, 9] for b in s):
        print(f"  VAddr 0x{pos:x} (offset 0x{pos:x}): {s.decode('latin1')}")
    pos = 0xcad00 + end + 1

# Now search for ADRP/ADD or LDR xrefs in .text to any address in [0xcade0, 0xcb050]
print("\n--- Finding XREFs in .text ---")
md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

# We can search for ADRP instructions and subsequent ADD / LDR
# In AArch64: ADRP Xd, #page; ADD Xd, Xd, #offset
# Let's disassemble .text and track registers

tracked_strings = [
    0xcadf0, # ps | grep "pppd -d file /etc/ppp/options_%s %s"
    0xcae18, # /bin/pppd -d file /etc/ppp/options_%s %s
    0xcae50, # /bin/ls /var/run | grep ppp%s.pid && kill...
    0xcaeb8, # /bin/ls /var/run | grep ppp%s.pid || /bin/pppd -d file /etc/ppp/options_%s %s &
    0xcaf08, # /bin/ls /var/run | grep ppp%s.pid || /bin/pppd file /etc/ppp/options_%s %s &
    0xcaf78, # /bin/ls /var/run | grep %s.pid || /bin/pppd file /etc/ppp/options_%s %s &
    0xcafc8  # /bin/ls /var/run | grep %s.pid && kill...
]

xrefs = []

# Scan instructions
# Keep map of reg -> page address
regs = {}

for insn in md.disasm(text_data, text_addr):
    # Check if ADRP
    if insn.mnemonic == 'adrp':
        reg = insn.operands[0].reg
        imm = insn.operands[1].imm
        regs[reg] = imm
    elif insn.mnemonic == 'add':
        if len(insn.operands) >= 3 and insn.operands[1].type == ARM64_OP_REG and insn.operands[2].type == ARM64_OP_IMM:
            src_reg = insn.operands[1].reg
            if src_reg in regs:
                target_addr = regs[src_reg] + insn.operands[2].imm
                dst_reg = insn.operands[0].reg
                regs[dst_reg] = target_addr
                for ts in tracked_strings:
                    if target_addr == ts or abs(target_addr - ts) < 4:
                        xrefs.append((insn.address, target_addr, insn))
        else:
            dst_reg = insn.operands[0].reg
            if dst_reg in regs:
                del regs[dst_reg]
    elif insn.mnemonic in ['b', 'bl', 'ret']:
        # Clear register tracking across branches/returns to prevent false positives across basic blocks
        if insn.mnemonic in ['b', 'ret']:
            regs.clear()
    else:
        # If destination register is modified, clear it from regs
        for op in insn.operands:
            if op.type == ARM64_OP_REG and insn.op_count(ARM64_OP_REG) > 0:
                # If modified
                pass

print(f"Found {len(xrefs)} direct ADRP+ADD xrefs:")
for code_addr, target_addr, insn in xrefs:
    # Find enclosing function
    fn_name = "unknown"
    fn_addr = 0
    for s_addr, s_size, s_name in symbols:
        if s_addr <= code_addr < (s_addr + s_size if s_size > 0 else s_addr + 0x1000):
            fn_name = s_name
            fn_addr = s_addr
            break
    print(f"  Code 0x{code_addr:x} -> Target 0x{target_addr:x} | Func: {fn_name} (0x{fn_addr:x}) | insn: {insn.mnemonic} {insn.op_str}")


