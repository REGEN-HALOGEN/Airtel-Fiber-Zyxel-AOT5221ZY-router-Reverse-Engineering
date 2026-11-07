import lzma
import struct
import os

with open(r'C:\Users\REGEN\AirtelModemRev\files\config.rdm', 'rb') as f:
    raw = f.read()

data = lzma.decompress(raw, format=lzma.FORMAT_ALONE)
print(f'Decompressed size: {len(data)}')

# Search for WANConnectionDevice, WANPPPConnection, WANIPConnection in data
keywords = [b'WANConnectionDevice', b'WANPPPConnection', b'WANIPConnection', b'WANEthernetInterfaceConfig', b'WANDevice']

for kw in keywords:
    pos = 0
    matches = []
    while True:
        idx = data.find(kw, pos)
        if idx == -1:
            break
        matches.append(idx)
        pos = idx + len(kw)
    print(f'{kw.decode()}: {len(matches)} matches, first at 0x{matches[0]:x}')

# Inspect surrounding bytes for WANPPPConnection
idx = data.find(b'WANPPPConnection')
snippet = data[idx-64 : idx+128]
print('Surrounding WANPPPConnection:')
for i in range(0, len(snippet), 16):
    chunk = snippet[i:i+16]
    h = ' '.join(f'{b:02x}' for b in chunk)
    a = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f'{h:<48} {a}')

