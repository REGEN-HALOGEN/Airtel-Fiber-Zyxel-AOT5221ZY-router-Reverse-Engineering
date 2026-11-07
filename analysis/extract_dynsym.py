#!/usr/bin/env python3
"""Extract dynamic symbols from ELF binaries and filter for PPP/WAN related symbols."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

FILES_DIR = r"C:\Users\REGEN\AirtelModemRev\files"
OUT_DIR = r"C:\Users\REGEN\AirtelModemRev\analysis"

PPP_KEYWORDS = [
    'PPP', 'ppp', 'PPPoE', 'pppoe', 'WAN', 'wan', 'Connection', 'connection',
    'SMUX', 'smux', 'nas', 'Auth', 'auth', 'PAP', 'CHAP', 'MTU', 'MRU',
    'ServiceName', 'service_name', 'Service', 'service',
    'Callback', 'callback', 'Register', 'register',
    'RDM', 'rdm', 'Object', 'obj', 'Event', 'event',
    'Username', 'Password', 'VLAN', 'vlan', 'Device', 'device',
    'Ethernet', 'ethernet', 'ACName', 'pppd', 'smuxctl',
    'ConnectionDevice', 'Dial', 'dial', 'LCP', 'lcp', 'IPCP', 'ipcp',
    'NCP', 'ncp', 'Link', 'link', 'Session', 'session',
]

def extract_symbols(filepath, section_names=['.dynsym', '.symtab']):
    """Extract all symbols from specified sections."""
    symbols = []
    with open(filepath, 'rb') as f:
        elf = ELFFile(f)
        for section in elf.iter_sections():
            if isinstance(section, SymbolTableSection) and section.name in section_names:
                for sym in section.iter_symbols():
                    name = sym.name
                    if not name:
                        continue
                    stype = sym.entry['st_info']['type']
                    bind = sym.entry['st_info']['bind']
                    value = sym.entry['st_value']
                    size = sym.entry['st_size']
                    shndx = sym.entry['st_shndx']
                    symbols.append({
                        'name': name,
                        'type': stype,
                        'bind': bind,
                        'value': value,
                        'size': size,
                        'shndx': shndx,
                        'section': section.name
                    })
    return symbols

def filter_ppp_symbols(symbols, keywords=PPP_KEYWORDS):
    """Filter symbols matching PPP/WAN keywords."""
    matched = []
    for sym in symbols:
        name_lower = sym['name'].lower()
        for kw in keywords:
            if kw.lower() in name_lower:
                matched.append(sym)
                break
    return matched

def format_symbol(sym):
    """Format a symbol for output."""
    defined = "DEF" if sym['shndx'] != 'SHN_UNDEF' else "UND"
    return f"  {defined} {sym['bind']:6s} {sym['type']:7s} 0x{sym['value']:016x} {sym['size']:8d}  {sym['name']}"

def process_binary(binary_name, output_name, sections=['.dynsym']):
    filepath = os.path.join(FILES_DIR, binary_name)
    outpath = os.path.join(OUT_DIR, output_name)
    
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} not found")
        return
    
    print(f"Processing {binary_name}...")
    symbols = extract_symbols(filepath, sections)
    ppp_symbols = filter_ppp_symbols(symbols)
    
    with open(outpath, 'w', encoding='utf-8') as out:
        out.write(f"{'='*80}\n")
        out.write(f"DYNAMIC SYMBOL EXTRACTION: {binary_name}\n")
        out.write(f"{'='*80}\n")
        out.write(f"Total symbols extracted: {len(symbols)}\n")
        out.write(f"PPP/WAN related symbols: {len(ppp_symbols)}\n\n")
        
        # PPP/WAN related symbols
        out.write(f"{'='*80}\n")
        out.write(f"PPP/WAN/CONNECTION RELATED SYMBOLS\n")
        out.write(f"{'='*80}\n")
        out.write(f"  {'STATUS':3s} {'BIND':6s} {'TYPE':7s} {'VALUE':18s} {'SIZE':8s}  NAME\n")
        out.write(f"  {'-'*3} {'-'*6} {'-'*7} {'-'*18} {'-'*8}  {'-'*40}\n")
        
        # Sort by name
        ppp_symbols.sort(key=lambda s: s['name'])
        for sym in ppp_symbols:
            out.write(format_symbol(sym) + '\n')
        
        out.write(f"\n{'='*80}\n")
        out.write(f"ALL SYMBOLS (sorted by name)\n")
        out.write(f"{'='*80}\n")
        symbols.sort(key=lambda s: s['name'])
        for sym in symbols:
            out.write(format_symbol(sym) + '\n')
    
    print(f"  -> {len(symbols)} total, {len(ppp_symbols)} PPP/WAN related -> {outpath}")
    return symbols, ppp_symbols

# Process each binary
results = {}

# 1. libbemodules.so
r = process_binary("libbemodules.so", "dynsym_libbemodules.txt")
if r: results['libbemodules'] = r

# 2. libcccbe.so
r = process_binary("libcccbe.so", "dynsym_libcccbe.txt")
if r: results['libcccbe'] = r

# 3. ccc_be
r = process_binary("ccc_be", "dynsym_ccc_be.txt")
if r: results['ccc_be'] = r

# 4. libcccrdm.so
r = process_binary("libcccrdm.so", "dynsym_libcccrdm.txt")
if r: results['libcccrdm'] = r

# 5. libbeEvents.so
r = process_binary("libbeEvents.so", "dynsym_libbeEvents.txt")
if r: results['libbeEvents'] = r

print("\n=== SUMMARY ===")
for name, (all_syms, ppp_syms) in results.items():
    print(f"  {name}: {len(all_syms)} total, {len(ppp_syms)} PPP/WAN related")
