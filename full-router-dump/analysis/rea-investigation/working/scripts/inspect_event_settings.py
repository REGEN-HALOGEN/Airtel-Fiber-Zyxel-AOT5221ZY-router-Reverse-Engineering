import struct
import elftools.elf.elffile as elffile

with open('full-router-dump/filesystem/rootfs/lib/MSTC/libbeEvents.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    dynsym = elf.get_section_by_name('.dynsym')
    syms = {s.name: s.entry.st_value for s in dynsym.iter_symbols()}
    
    settings = [
        'Route_EventSettingStruct',
        'NAT_EventSettingStruct',
        'Firewall_EventSettingStruct',
        'DNS_EventSettingStruct',
        'L3Forwarding_Connection_EventSettingStruct',
        'WANConnection_EventSettingStruct'
    ]
    
    for s_name in settings:
        addr = syms[s_name]
        sec = None
        for s in elf.iter_sections():
            if s['sh_addr'] <= addr < s['sh_addr'] + s['sh_size']:
                sec = s
                break
        data = sec.data()
        offset = addr - sec['sh_addr']
        # Print entries: often struct is {uint32_t event_id, uint32_t flags, uint64_t handler_func, ...}
        print(f"=== {s_name} at {hex(addr)} ===")
        for i in range(0, 48, 16):
            entry = data[offset+i:offset+i+16]
            ev_id, flags, h_ptr = struct.unpack('<IIQ', entry)
            # Find symbol for h_ptr
            h_name = ""
            for name, val in syms.items():
                if val == h_ptr:
                    h_name = name
                    break
            print(f"  EventID={ev_id} Flags={hex(flags)} Handler={hex(h_ptr)} <{h_name}>")
            if ev_id == 0:
                break

