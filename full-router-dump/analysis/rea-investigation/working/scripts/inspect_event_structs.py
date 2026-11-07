import struct
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.name: s.entry.st_value for s in dynsym.iter_symbols()}
    
    data_sec = None
    for s in elf.iter_sections():
        if s['sh_flags'] & 2: # alloc
            pass

    # Read data from section containing symbols
    for s_name in ['Route_RegEventStruct', 'NAT_RegEventStruct', 'Firewall_RegEventStruct', 'DNS_RegEventStruct', 'L3Forwarding_RegEventStruct', 'WAN_RegEventStruct']:
        addr = syms[s_name]
        # find section
        sec = None
        for s in elf.iter_sections():
            if s['sh_addr'] <= addr < s['sh_addr'] + s['sh_size']:
                sec = s
                break
        data = sec.data()
        offset = addr - sec['sh_addr']
        # Print first 64 bytes as ints
        chunk = data[offset:offset+64]
        ints = struct.unpack('<16I', chunk[:64])
        print(f"=== {s_name} at {hex(addr)} ===")
        print("  Values:", [i for i in ints if i != 0])

