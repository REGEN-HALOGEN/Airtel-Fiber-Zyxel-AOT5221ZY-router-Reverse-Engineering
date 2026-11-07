import struct
from elftools.elf.elffile import ELFFile

libcmd_path = r'full-router-dump\filesystem\rootfs\lib\MSTC\libCmd.so'

with open(libcmd_path, 'rb') as f:
    elf = ELFFile(f)
    rodata_sec = elf.get_section_by_name('.rodata')
    ro_data = rodata_sec.data()
    ro_base = rodata_sec['sh_addr']
    
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s['st_value']: s.name for s in dynsym.iter_symbols() if s['st_value'] != 0}

    # Inspect .data or .data.rel.ro at 0x12c220
    # In section table:
    # .data is 0x12bcf0 - 0x131e78 (offset 0x11bcf0)
    data_sec = elf.get_section_by_name('.data')
    d_data = data_sec.data()
    d_base = data_sec['sh_addr']
    d_offset = data_sec['sh_offset']

# Entry at 0x12c220:
off = 0x12c220 - d_base
chunk = d_data[off:off+256]

print(f"Table at 0x12c220 (offset 0x{off:x}):")
# Usually struct cmd_entry { char *cmd_name; int (*func)(...); char *help; ... }
# In 64-bit: 8 bytes ptr, 8 bytes ptr, ...
for i in range(0, len(chunk), 32):
    q = struct.unpack('<QQQQ', chunk[i:i+32])
    # check if q[0] is in rodata
    name = ""
    if ro_base <= q[0] < ro_base + len(ro_data):
        r_off = q[0] - ro_base
        name = ro_data[r_off:ro_data.find(b'\x00', r_off)].decode('latin1', errors='ignore')
    fn_name = syms.get(q[1], f"0x{q[1]:x}")
    print(f"  +0x{i:02x}: name_ptr=0x{q[0]:x} (\"{name}\"), func_ptr=0x{q[1]:x} ({fn_name}), q2=0x{q[2]:x}, q3=0x{q[3]:x}")


