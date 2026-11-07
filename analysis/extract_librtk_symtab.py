#!/usr/bin/env python3
"""Extract full symbol table from librtk.so (has .symtab + debug info)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

FILES_DIR = r"C:\Users\REGEN\AirtelModemRev\files"
OUT_DIR = r"C:\Users\REGEN\AirtelModemRev\analysis"

PPP_KEYWORDS = [
    'PPP', 'ppp', 'PPPoE', 'pppoe', 'WAN', 'wan', 
    'SMUX', 'smux', 'nas', 'Ethernet', 'ethernet',
    'smuxctl', 'pppd', 'connection', 'Connection',
    'auth', 'Auth', 'PAP', 'CHAP', 'LCP', 'lcp',
    'IPCP', 'ipcp', 'NCP', 'ncp', 'MTU', 'MRU',
    'ServiceName', 'service_name', 'ACName',
    'Session', 'session', 'Dial', 'dial',
    'Link', 'link', 'Username', 'Password',
    'VLAN', 'vlan', 'Device', 'device',
    'Callback', 'callback', 'Register', 'register',
]

filepath = os.path.join(FILES_DIR, "librtk.so")
outpath = os.path.join(OUT_DIR, "symtab_librtk_ppp.txt")

print(f"Processing librtk.so (full symtab)...")

all_symbols = []
section_counts = {}

with open(filepath, 'rb') as f:
    elf = ELFFile(f)
    
    # List all sections
    print("Sections:")
    for section in elf.iter_sections():
        if isinstance(section, SymbolTableSection):
            count = section.num_symbols()
            section_counts[section.name] = count
            print(f"  {section.name}: {count} symbols")
    
    # Extract from both .symtab and .dynsym
    for section in elf.iter_sections():
        if isinstance(section, SymbolTableSection):
            for sym in section.iter_symbols():
                name = sym.name
                if not name:
                    continue
                stype = sym.entry['st_info']['type']
                bind = sym.entry['st_info']['bind']
                value = sym.entry['st_value']
                size = sym.entry['st_size']
                shndx = sym.entry['st_shndx']
                all_symbols.append({
                    'name': name,
                    'type': stype,
                    'bind': bind,
                    'value': value,
                    'size': size,
                    'shndx': shndx,
                    'section': section.name,
                })

# Filter PPP related
ppp_symbols = []
for sym in all_symbols:
    name_lower = sym['name'].lower()
    for kw in PPP_KEYWORDS:
        if kw.lower() in name_lower:
            ppp_symbols.append(sym)
            break

# Deduplicate by name+value
seen = set()
unique_ppp = []
for sym in ppp_symbols:
    key = (sym['name'], sym['value'])
    if key not in seen:
        seen.add(key)
        unique_ppp.append(sym)

unique_ppp.sort(key=lambda s: s['name'])

def format_sym(sym):
    defined = "DEF" if sym['shndx'] != 'SHN_UNDEF' else "UND"
    return f"  {defined} {sym['bind']:6s} {sym['type']:7s} 0x{sym['value']:016x} {sym['size']:8d}  {sym['name']}"

with open(outpath, 'w', encoding='utf-8') as out:
    out.write(f"{'='*100}\n")
    out.write(f"SYMBOL TABLE EXTRACTION: librtk.so (with full .symtab + debug info)\n")
    out.write(f"{'='*100}\n")
    out.write(f"Total symbols: {len(all_symbols)}\n")
    for sn, sc in section_counts.items():
        out.write(f"  {sn}: {sc} symbols\n")
    out.write(f"PPP/WAN related (unique): {len(unique_ppp)}\n\n")
    
    # Group by category
    categories = {
        'PPP Core': ['ppp', 'PPP'],
        'PPPoE': ['pppoe', 'PPPoE'],
        'WAN': ['wan', 'WAN'],
        'SMUX/NAS': ['smux', 'SMUX', 'nas', 'smuxctl'],
        'Auth (PAP/CHAP)': ['auth', 'Auth', 'PAP', 'CHAP', 'Username', 'Password'],
        'LCP/NCP/IPCP': ['LCP', 'lcp', 'NCP', 'ncp', 'IPCP', 'ipcp'],
        'MTU/MRU': ['MTU', 'MRU'],
        'Connection/Session': ['connection', 'Connection', 'session', 'Session', 'Dial', 'dial'],
        'Link/Device': ['link', 'Link', 'device', 'Device', 'Ethernet', 'ethernet'],
        'VLAN': ['vlan', 'VLAN'],
        'Service': ['ServiceName', 'service_name', 'ACName'],
        'Callback/Register': ['callback', 'Callback', 'register', 'Register'],
    }
    
    for cat_name, cat_kws in categories.items():
        cat_syms = []
        for sym in unique_ppp:
            name_lower = sym['name'].lower()
            for kw in cat_kws:
                if kw.lower() in name_lower:
                    cat_syms.append(sym)
                    break
        
        if cat_syms:
            out.write(f"\n{'='*100}\n")
            out.write(f"CATEGORY: {cat_name} ({len(cat_syms)} symbols)\n")
            out.write(f"{'='*100}\n")
            for sym in sorted(cat_syms, key=lambda s: s['name']):
                out.write(format_sym(sym) + '\n')
    
    # Full list
    out.write(f"\n{'='*100}\n")
    out.write(f"ALL PPP/WAN RELATED SYMBOLS (alphabetical, deduplicated)\n")
    out.write(f"{'='*100}\n")
    for sym in unique_ppp:
        out.write(format_sym(sym) + '\n')

print(f"  -> {len(all_symbols)} total, {len(unique_ppp)} PPP/WAN related (unique) -> {outpath}")
