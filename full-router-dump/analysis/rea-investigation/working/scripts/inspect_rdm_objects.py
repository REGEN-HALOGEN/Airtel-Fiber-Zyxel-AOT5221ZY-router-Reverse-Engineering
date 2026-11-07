import struct

path = r'c:\Users\REGEN\AirtelModemRev\analysis\config_rdm_decompressed.bin'
with open(path, 'rb') as f:
    data = f.read()

# Let's inspect objects:
keywords = [
    b'WANSwitch',
    b'WANEthernetInterfaceConfig',
    b'WANConnectionDevice',
    b'WANIPConnection',
    b'WANPPPConnection',
    b'Layer3Forwarding'
]

for kw in keywords:
    pos = 0
    found = []
    while True:
        idx = data.find(kw, pos)
        if idx == -1: break
        found.append(idx)
        pos = idx + len(kw)
    print(f'=== Keyword {kw.decode()} (matches: {len(found)}) ===')
    for idx in found[:3]:
        # print 32 bytes before and 48 bytes after
        snippet = data[max(0, idx-16) : min(len(data), idx+len(kw)+32)]
        h = ' '.join(f'{b:02x}' for b in snippet)
        a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in snippet)
        print(f'Offset 0x{idx:x}:')
        print(f'  Hex:   {h}')
        print(f'  Ascii: {a}')

