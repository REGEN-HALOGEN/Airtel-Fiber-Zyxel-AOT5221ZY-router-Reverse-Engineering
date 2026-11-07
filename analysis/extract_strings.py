#!/usr/bin/env python3
"""Extract printable strings from libbemodules.so and filter for PPP/WAN related."""
import os, re

FILES_DIR = r"C:\Users\REGEN\AirtelModemRev\files"
OUT_DIR = r"C:\Users\REGEN\AirtelModemRev\analysis"

SEARCH_KEYWORDS = [
    'PPP', 'pppoe', 'pppd', 'nas0', 'nas', 'smux', 'WAN', 'wan',
    'ServiceName', 'service', 'auth', 'Username', 'Password',
    'MTU', 'MRU', 'ACName', 'VLAN', 'vlan', 'connection',
    'device', 'Device', 'ConnectionDevice', 'ppp',
    'LCP', 'IPCP', 'CHAP', 'PAP', 'Session', 'Dial',
    'Link', 'Ethernet', 'ethernet', 'smuxctl',
    'X_ZYXEL', 'X_5067F0', 'oid', 'OID',
    'RDM', 'rdm', 'callback', 'register',
]

def extract_strings(filepath, min_length=6):
    """Extract printable ASCII strings from binary."""
    strings = []
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find runs of printable ASCII characters
    pattern = re.compile(rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}')
    for match in pattern.finditer(data):
        offset = match.start()
        s = match.group().decode('ascii', errors='replace')
        strings.append((offset, s))
    
    return strings

def filter_strings(strings, keywords):
    """Filter strings matching keywords."""
    matched = []
    for offset, s in strings:
        s_lower = s.lower()
        for kw in keywords:
            if kw.lower() in s_lower:
                matched.append((offset, s, kw))
                break
    return matched

filepath = os.path.join(FILES_DIR, "libbemodules.so")
outpath = os.path.join(OUT_DIR, "strings_libbemodules_ppp.txt")

print(f"Extracting strings from libbemodules.so...")
all_strings = extract_strings(filepath, min_length=6)
ppp_strings = filter_strings(all_strings, SEARCH_KEYWORDS)

# Deduplicate by string content
seen = set()
unique_ppp = []
for offset, s, kw in ppp_strings:
    if s not in seen:
        seen.add(s)
        unique_ppp.append((offset, s, kw))

unique_ppp.sort(key=lambda x: x[1].lower())

with open(outpath, 'w', encoding='utf-8') as out:
    out.write(f"{'='*100}\n")
    out.write(f"STRING EXTRACTION: libbemodules.so\n")
    out.write(f"{'='*100}\n")
    out.write(f"Total strings (>= 6 chars): {len(all_strings)}\n")
    out.write(f"PPP/WAN related strings (unique): {len(unique_ppp)}\n\n")
    
    # Group by keyword category
    groups = {}
    for offset, s, kw in unique_ppp:
        groups.setdefault(kw, []).append((offset, s))
    
    for kw in sorted(groups.keys()):
        entries = groups[kw]
        out.write(f"\n--- Matched keyword: '{kw}' ({len(entries)} strings) ---\n")
        for offset, s in sorted(entries, key=lambda x: x[1]):
            out.write(f"  0x{offset:08x}: {s}\n")
    
    out.write(f"\n{'='*100}\n")
    out.write(f"ALL PPP/WAN RELATED STRINGS (alphabetical, deduplicated)\n")
    out.write(f"{'='*100}\n")
    for offset, s, kw in unique_ppp:
        out.write(f"  0x{offset:08x} [{kw:20s}]: {s}\n")

# Also extract from other interesting binaries for cross-reference
for extra_bin in ['libcccbe.so', 'ccc_be', 'libbeEvents.so']:
    extra_path = os.path.join(FILES_DIR, extra_bin)
    if os.path.exists(extra_path):
        extra_strings = extract_strings(extra_path, min_length=6)
        extra_ppp = filter_strings(extra_strings, SEARCH_KEYWORDS)
        print(f"  {extra_bin}: {len(extra_strings)} total strings, {len(extra_ppp)} PPP/WAN related")
        
        # Append to main output
        with open(outpath, 'a', encoding='utf-8') as out:
            out.write(f"\n\n{'='*100}\n")
            out.write(f"CROSS-REFERENCE STRINGS: {extra_bin}\n")
            out.write(f"{'='*100}\n")
            seen2 = set()
            for offset, s, kw in extra_ppp:
                if s not in seen2:
                    seen2.add(s)
                    out.write(f"  0x{offset:08x} [{kw:20s}]: {s}\n")

print(f"\nDone. -> {outpath}")
