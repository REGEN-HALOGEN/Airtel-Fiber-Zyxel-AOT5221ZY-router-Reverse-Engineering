import elftools.elf.elffile as elffile
import struct

with open('full-router-dump/filesystem/rootfs/lib/MSTC/librdm.so', 'rb') as f:
    elf = elffile.ELFFile(f)
    symtab = elf.get_section_by_name('.dynsym')
    oid_table_sym = None
    for sym in symtab.iter_symbols():
        if sym.name == 'OIDTable':
            oid_table_sym = sym
            break
    
    sec = None
    for s in elf.iter_sections():
        if s['sh_addr'] <= oid_table_sym['st_value'] < s['sh_addr'] + s['sh_size']:
            sec = s
            break
            
    data = sec.data()
    offset = oid_table_sym['st_value'] - sec['sh_addr']
    table_bytes = data[offset:offset+oid_table_sym['st_size']]
    print(f"OIDTable size: {len(table_bytes)} bytes")

    rodata = elf.get_section_by_name('.rodata')
    ro_data = rodata.data()
    ro_addr = rodata['sh_addr']

    # Let's see entry size. In previous script inspect_oid_table.py let's see how entries were formatted.
    # Let's search for specific OIDs: 0xc7, 0xca, 0x44, 0x45, 0xcd, 0xd5, 0x199, 0x8a
    target_oids = [0xc7, 0xca, 0x44, 0x45, 0xcd, 0xd5, 0x199, 0x8a, 0x73, 0x24, 0x30, 0x6a]
    
    # Let's check entry stride: in 64-bit MSTC OIDTable, what is the stride?
    # Let's search where OID appears at stride multiples
    for stride in [32, 40, 48, 56, 64, 72, 80]:
        matches = 0
        for i in range(0, min(len(table_bytes), 2000), stride):
            oid = struct.unpack('<I', table_bytes[i:i+4])[0]
            if 0 < oid < 1000:
                matches += 1
        if matches > 10:
            print(f"Candidate stride: {stride} (matches: {matches})")
