import lzma
import struct

with open(r'C:\Users\REGEN\AirtelModemRev\files\config.rdm', 'rb') as f:
    raw = f.read()

data = lzma.decompress(raw, format=lzma.FORMAT_ALONE)

# Let's inspect the block from 0x36900 to 0x38000
start = 0x36900
end = 0x38000
sub = data[start:end]

# Find all ASCII strings of length >= 3
idx = 0
strings = []
while idx < len(sub):
    if 32 <= sub[idx] < 127:
        s_start = idx
        while idx < len(sub) and 32 <= sub[idx] < 127:
            idx += 1
        s = sub[s_start:idx].decode('latin1')
        if len(s) >= 3:
            strings.append((start + s_start, s))
    else:
        idx += 1

print(f'Found {len(strings)} strings in range 0x{start:x}-0x{end:x}:')
for addr, s in strings[:100]:
    print(f'0x{addr:x}: {s}')

